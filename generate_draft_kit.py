import os
import sys
import json
import duckdb
import pandas as pd
import numpy as np
from scrape_projections import fetch_enriched_projections
from market_consensus import get_sleeper_market_adp

def generate_blended_top_100(db_path: str = "fantasy_analytics.db") -> dict:
    """
    Calculates 50/50 composite VORP calibrated specifically to match 
    10-Team Half-PPR consensus rankings (Rotoworld baseline).
    """
    print("=" * 65)
    print("🏈 GENERATING ROTOWORLD-ALIGNED TOP 100 BIG BOARD")
    print("=" * 65)

    # 1. Fetch Enriched Model Projections from DuckDB
    df_model = fetch_enriched_projections(db_path)
    
    # Filter strictly for skill positions (QB, RB, WR, TE)
    df_model = df_model[df_model['position'].isin(['QB', 'RB', 'WR', 'TE'])].copy()

    # 2. Fetch Live Sleeper Market ADP Consensus
    df_market = get_sleeper_market_adp()

    # 3. Dynamic Name Key Join
    if not df_market.empty:
        df_merged = pd.merge(
            df_model, 
            df_market[['match_key', 'position', 'market_adp', 'market_pos_rank']], 
            on=['match_key', 'position'], 
            how='left'
        )
    else:
        df_merged = df_model.copy()
        df_merged['market_adp'] = 250.0
        df_merged['market_pos_rank'] = 99.0

    df_merged['market_adp'] = df_merged['market_adp'].fillna(200.0)
    df_merged['market_pos_rank'] = df_merged['market_pos_rank'].fillna(60.0)

    # 4. Replacement Baselines (10-Team Half-PPR: 1 QB, 2 RB, 2 WR, 1 TE, 1 Flex)
    baselines = {
        'QB': 10,   # QB10 replacement
        'RB': 28,   # RB28 (Starters + Flex)
        'WR': 29,   # WR29 (Starters + Flex)
        'TE': 10    # TE10 replacement
    }

    # Model VORP Calculation
    model_baselines = {}
    for pos, rank in baselines.items():
        pos_df = df_merged[df_merged['position'] == pos].sort_values('adjusted_season_xfp', ascending=False)
        model_baselines[pos] = pos_df.iloc[rank - 1]['adjusted_season_xfp'] if len(pos_df) >= rank else 0.0

    df_merged['model_vorp_raw'] = df_merged['adjusted_season_xfp'] - df_merged['position'].map(model_baselines)

    # 5. Market VORP Calibration (Matching Rotoworld Draft Curve)
    # Uses exponential decay model mapped to draft capital rather than linear VBD
    df_merged['market_points_est'] = np.maximum(0, 210.0 * np.exp(-0.016 * df_merged['market_adp']))

    market_baselines = {}
    for pos, rank in baselines.items():
        pos_df = df_merged[df_merged['position'] == pos].sort_values('market_points_est', ascending=False)
        market_baselines[pos] = pos_df.iloc[rank - 1]['market_points_est'] if len(pos_df) >= rank else 0.0

    df_merged['market_vorp_raw'] = df_merged['market_points_est'] - df_merged['position'].map(market_baselines)

    # 6. Positional Weighting (Calibrated against Rotoworld Top 100)
    # RBs & WRs drive high early-round demand; TEs and QBs are dampened to match target ranks
    pos_weights = {
        'RB': 1.00,
        'WR': 1.00,
        'QB': 0.42,  # Places QB1 (Allen) around #30-#35 overall
        'TE': 0.52   # Places TE1 (Bowers) around #15-#20 overall
    }
    df_merged['pos_weight'] = df_merged['position'].map(pos_weights)

    df_merged['model_vorp'] = df_merged['model_vorp_raw'] * df_merged['pos_weight']
    df_merged['market_vorp'] = df_merged['market_vorp_raw'] * df_merged['pos_weight']

    # 7. 50/50 Composite Blend
    df_merged['composite_vorp'] = (0.5 * df_merged['model_vorp']) + (0.5 * df_merged['market_vorp'])
    df_merged['composite_vorp'] = df_merged['composite_vorp'].round(2)

    # Sort Overall Big Board
    df_sorted = df_merged.sort_values('composite_vorp', ascending=False).reset_index(drop=True)
    df_sorted['overall_rank'] = df_sorted.index + 1

    # Safe Positional Breakdown Extraction
    rankings_by_pos = {}
    for pos in ['QB', 'RB', 'WR', 'TE']:
        pos_df = df_sorted[df_sorted['position'] == pos].copy().reset_index(drop=True)
        pos_df['pos_rank'] = pos_df.index + 1
        rankings_by_pos[pos] = pos_df

    print("\n[3/3] Successfully generated calibrated Top 100 Overall Big Board.")
    return {
        "df_top_100": df_sorted.head(100),
        "rankings_by_pos": rankings_by_pos,
        "baselines_used": {"model": model_baselines, "market": market_baselines}
    }

if __name__ == "__main__":
    kit = generate_blended_top_100()
    df_top = kit['df_top_100']

    cols = ['overall_rank', 'player_name', 'position', 'team', 'adjusted_season_xfp', 'market_adp', 'composite_vorp']
    
    print("\n" + "=" * 75)
    print("🏆 ROTOWORLD-ALIGNED TOP 30 OVERALL BIG BOARD")
    print("=" * 75)
    print(df_top[cols].head(30).to_string(index=False))

    print("\n" + "=" * 75)
    print("🏈 TOP 5 BY POSITION BREAKDOWN")
    print("=" * 75)
    for pos in ['QB', 'RB', 'WR', 'TE']:
        pos_df = kit['rankings_by_pos'][pos].head(5)
        print(f"\n--- TOP 5 {pos}s ---")
        if not pos_df.empty:
            print(pos_df[['pos_rank', 'overall_rank', 'player_name', 'team', 'composite_vorp']].to_string(index=False))