import duckdb
import pandas as pd
import numpy as np
import re

def create_match_key(name: str) -> str:
    """Normalizes 'W. Robinson' or 'Wan'Dale Robinson' to 'wrobinson' for joining."""
    if not name:
        return ""
    parts = name.strip().split()
    if len(parts) >= 2:
        first_init = re.sub(r"[^a-zA-Z]", "", parts[0])[0].lower() if parts[0] else ""
        last_name = re.sub(r"[^a-zA-Z]", "", "".join(parts[1:])).lower()
        return f"{first_init}{last_name}"
    return re.sub(r"[^a-zA-Z]", "", name).lower()

def fetch_enriched_projections(db_path: str = "fantasy_analytics.db") -> pd.DataFrame:
    con = duckdb.connect(db_path, read_only=True)
    
    cols_df = con.execute("PRAGMA table_info('v_2026_contextual_projections')").df()
    available_cols = set(cols_df['name'].tolist())
    
    def col_sql(col_name: str, fallback: str = "0.0") -> str:
        return f"COALESCE({col_name}, {fallback})" if col_name in available_cols else fallback

    player_id_select = "player_id," if "player_id" in available_cols else "player_name AS player_id,"

    query = f"""
    SELECT 
        {player_id_select}
        player_name,
        position,
        COALESCE(new_team, old_team) AS team,
        
        COALESCE(proj_2026_xfp_pg, 0.0) AS xfp_pg,
        COALESCE(proj_2026_xfp_pg, 0.0) * 17.0 AS proj_season_xfp,
        COALESCE(proj_2026_target_share, 0.0) AS target_share,
        
        {col_sql('proj_2026_air_yard_share')} AS air_yard_share,
        {col_sql('proj_2026_adot')} AS adot,
        {col_sql('proj_2026_wopr')} AS wopr,
        {col_sql('proj_2026_first_read_share')} AS first_read_share,
        {col_sql('proj_2026_yprr')} AS yprr
        
    FROM v_2026_contextual_projections
    WHERE position IN ('QB', 'RB', 'WR', 'TE')
    """
    
    df = con.execute(query).df()
    con.close()

    # Create join key for market matching
    df['match_key'] = df['player_name'].apply(create_match_key)

    # 1. Forward-Looking WOPR
    df['wopr'] = np.where(
        df['wopr'] == 0, 
        (1.5 * df['target_share']) + (0.7 * df['air_yard_share']), 
        df['wopr']
    )

    # 2. Forward-Looking Efficiency & Depth Multiplier
    # Receivers with aDOT < 8.0 and target share under 20% are penalized up to 40%
    adot_factor = np.clip(df['adot'] / 10.0, 0.50, 1.20)
    wopr_factor = np.clip(df['wopr'] / 0.50, 0.60, 1.25)
    
    df['forward_quality_multiplier'] = np.where(
        df['position'] == 'WR',
        adot_factor * wopr_factor,
        1.0
    )

    df['adjusted_xfp_pg'] = df['xfp_pg'] * df['forward_quality_multiplier']
    df['adjusted_season_xfp'] = df['adjusted_xfp_pg'] * 17.0

    return df