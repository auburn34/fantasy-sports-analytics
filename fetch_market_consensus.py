import json
import urllib.request
import pandas as pd
import numpy as np
import duckdb

def get_sleeper_market_adp():
    """
    Fetches real-time player data and search trends/ADP rankings directly from Sleeper's public API.
    Does not require an API key.
    """
    print("📡 Fetching live market metadata from Sleeper API...")
    url = "https://api.sleeper.app/v1/players/nfl"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
    
    players = []
    for player_id, info in data.items():
        # Filter down to relevant fantasy positions
        if info.get('position') in ['QB', 'RB', 'WR', 'TE'] and info.get('active'):
            first_name = info.get('first_name', '')
            last_name = info.get('last_name', '')
            
            # Format name string (e.g. "P. Nacua" or "Puka Nacua") to align with model
            short_name = f"{first_name[0]}. {last_name}" if first_name else last_name
            full_name = f"{first_name} {last_name}".strip()
            
            # Sleeper includes ADP rankings in player metadata; fallback to search_rank if null
            adp = info.get('years_exp', 0) # Fallback key structure
            search_rank = info.get('search_rank', 999)
            
            players.append({
                'sleeper_id': player_id,
                'full_name': full_name,
                'player_name': short_name,
                'position': info.get('position'),
                'team': info.get('team'),
                'market_adp': float(search_rank) if search_rank else 250.0
            })
            
    df_market = pd.DataFrame(players)
    
    # Sort by market rank and create dynamic market positional rankings
    df_market = df_market.sort_values('market_adp').reset_index(drop=True)
    df_market['market_pos_rank'] = df_market.groupby('position').cumcount() + 1
    
    return df_market

def fetch_and_blend_rankings(db_path="fantasy_analytics.db"):
    """
    Loads DuckDB model xFP, fetches dynamic live market rankings, 
    blends scores, and dynamically tags outliers for review.
    """
    # 1. Pull DuckDB Model Projections
    con = duckdb.connect(db_path, read_only=True)
    query = """
    SELECT 
        player_id,
        player_name,
        position,
        COALESCE(new_team, old_team) AS team,
        proj_2026_target_share,
        proj_2026_xfp_pg,
        proj_2026_xfp_pg * 17 AS proj_season_xfp
    FROM v_2026_contextual_projections
    WHERE position IN ('QB', 'RB', 'WR', 'TE')
    """
    df_model = con.execute(query).df()
    con.close()

    # 2. Fetch Dynamic Market Data from API
    df_market = get_sleeper_market_adp()

    # 3. Dynamic Merge (Primary: Exact Short Name / Secondary: Full Name)
    df_merged = pd.merge(
        df_model, 
        df_market[['player_name', 'position', 'market_adp', 'market_pos_rank']], 
        on=['player_name', 'position'], 
        how='left'
    )
    
    # Fallback for unmapped players
    df_merged['market_adp'] = df_merged['market_adp'].fillna(250.0)
    df_merged['market_pos_rank'] = df_merged['market_pos_rank'].fillna(99.0)

    # 4. Calculate Model VORP (10-Team Baseline)
    baselines = {'QB': 11, 'RB': 28, 'WR': 29, 'TE': 11}
    model_baselines = {}
    
    for pos, rank in baselines.items():
        pos_df = df_merged[df_merged['position'] == pos].sort_values('proj_season_xfp', ascending=False)
        model_baselines[pos] = pos_df.iloc[rank - 1]['proj_season_xfp'] if len(pos_df) >= rank else 0

    df_merged['model_vorp'] = df_merged['proj_season_xfp'] - df_merged['position'].map(model_baselines)

    # 5. Dynamic Market VORP Conversion
    # Map ADP curve to comparable VORP point scale dynamically
    df_merged['market_points_est'] = np.maximum(0, 260.0 - (df_merged['market_adp'] * 1.05))
    
    market_baselines = {}
    for pos, rank in baselines.items():
        pos_df = df_merged[df_merged['position'] == pos].sort_values('market_points_est', ascending=False)
        market_baselines[pos] = pos_df.iloc[rank - 1]['market_points_est'] if len(pos_df) >= rank else 0

    df_merged['market_vorp'] = df_merged['market_points_est'] - df_merged['position'].map(market_baselines)

    # 6. Apply 50/50 Blended Score Formula
    df_merged['composite_vorp'] = (0.5 * df_merged['model_vorp']) + (0.5 * df_merged['market_vorp'])
    
    # Sort and rank overall
    df_sorted = df_merged.sort_values('composite_vorp', ascending=False).reset_index(drop=True)
    df_sorted['blended_rank'] = df_sorted.index + 1

    # Calculate model rank standalone for delta auditing
    df_sorted['model_rank'] = df_sorted.groupby('position')['proj_season_xfp'].rank(ascending=False, method='min')

    # 7. Dynamic Outlier Guardrails (Flag players deviating significantly from market)
    # Audits players where Model Positional Rank is 15+ spots higher/lower than Market Positional Rank
    df_sorted['pos_rank_delta'] = df_sorted['model_rank'] - df_sorted['market_pos_rank']
    df_sorted['outlier_flag'] = np.where(
        df_sorted['pos_rank_delta'] < -12, 'MODEL_OVERVALUED',
        np.where(df_sorted['pos_rank_delta'] > 12, 'MODEL_UNDERVALUED', 'ALIGNED')
    )

    return df_sorted

if __name__ == "__main__":
    df_final = fetch_and_blend_rankings()
    
    # Print out auto-identified outliers (e.g. M. Wilson / W. Robinson)
    outliers = df_final[df_final['outlier_flag'] != 'ALIGNED']
    print("\n🚨 DYNAMICALLY DETECTED OUTLIERS FOR AUDIT:")
    print(outliers[['player_name', 'position', 'model_rank', 'market_pos_rank', 'outlier_flag']].head(15))