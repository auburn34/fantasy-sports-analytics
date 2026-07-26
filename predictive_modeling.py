import duckdb
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

def run_predictive_modeling():
    con = duckdb.connect("fantasy_analytics.db")
    print("=" * 75)
    print("🤖 EXECUTING FANTASY ANALYTICS PREDICTIVE MODELING ENGINE")
    print("=" * 75)

    # -------------------------------------------------------------------
    # STEP 1: HISTORICAL MACHINE LEARNING MODEL (Year N -> Year N+1)
    # -------------------------------------------------------------------
    print("\n[1/3] Training Year-over-Year (YoY) Random Forest Model...")
    
    yoy_query = """
    WITH yearly_summary AS (
        SELECT 
            season,
            player_name,
            position,
            historical_team,
            COUNT(*) AS gms,
            ROUND(AVG(target_share_pct), 1) AS avg_target_share,
            ROUND(AVG(air_yard_share_pct), 1) AS avg_air_share,
            ROUND(AVG(wopr), 2) AS avg_wopr,
            ROUND(AVG(adot), 1) AS avg_adot,
            ROUND(AVG(racr), 2) AS avg_racr,
            ROUND(AVG(expected_half_ppr_pts), 1) AS avg_xfp,
            ROUND(AVG(actual_half_ppr_pts), 1) AS avg_fppg,
            ROUND(AVG(fpoe), 1) AS avg_fpoe,
            ROUND(AVG(targets), 1) AS avg_targets
        FROM v_master_fantasy_analytics_50
        WHERE position IN ('WR', 'TE', 'RB')
        GROUP BY season, player_name, position, historical_team
        HAVING COUNT(*) >= 5
    )
    SELECT 
        curr.player_name,
        curr.position,
        curr.season AS yr_n,
        curr.avg_wopr AS wopr_n,
        curr.avg_target_share AS target_share_n,
        curr.avg_air_share AS air_share_n,
        curr.avg_xfp AS xfp_n,
        curr.avg_fppg AS fppg_n,
        curr.avg_fpoe AS fpoe_n,
        curr.avg_adot AS adot_n,
        curr.avg_racr AS racr_n,
        nxt.avg_fppg AS fppg_n1_target
    FROM yearly_summary curr
    INNER JOIN yearly_summary nxt
        ON curr.player_name = nxt.player_name
       AND nxt.season = curr.season + 1;
    """

    df_yoy = con.execute(yoy_query).df()

    if not df_yoy.empty and len(df_yoy) >= 20:
        features = ['wopr_n', 'target_share_n', 'air_share_n', 'xfp_n', 'fppg_n', 'fpoe_n', 'adot_n', 'racr_n']
        X = df_yoy[features].fillna(0)
        y = df_yoy['fppg_n1_target']

        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X, y)

        importances = pd.Series(rf_model.feature_importances_, index=features).sort_values(ascending=False)
        print("\n--- 📊 FEATURE IMPORTANCE (Predicting Next Year's Fantasy PPG) ---")
        for feat, imp in importances.items():
            print(f"  • {feat:<18}: {imp*100:.1f}% influence")
    else:
        print("⚠️ Insufficient multi-season historical data for ML training. Skipping feature importance fitting.")

    # -------------------------------------------------------------------
    # STEP 2: 2026 HISTORICAL BUY-LOW & SELL-HIGH CANDIDATES
    # -------------------------------------------------------------------
    print("\n" + "="*75)
    print("🔥 2026 BREAKOUT / BUY-LOW CANDIDATES (High Opportunity WOPR & xFP vs Actuals)")
    print("="*75)

    breakouts_query = """
    SELECT 
        player_name,
        position,
        team AS current_team,
        historical_team AS old_team,
        COUNT(*) AS games_played,
        ROUND(AVG(wopr), 2) AS wopr_2025,
        ROUND(AVG(target_share_pct), 1) AS target_share_2025,
        ROUND(AVG(expected_half_ppr_pts), 1) AS expected_fppg,
        ROUND(AVG(actual_half_ppr_pts), 1) AS actual_fppg,
        ROUND(AVG(fpoe), 1) AS fpoe_per_game
    FROM v_master_fantasy_analytics_50
    WHERE season = 2025 AND position IN ('WR', 'TE')
    GROUP BY player_name, position, team, historical_team
    HAVING COUNT(*) >= 5 AND AVG(wopr) >= 0.55
    ORDER BY fpoe_per_game ASC
    LIMIT 10;
    """
    df_breakouts = con.execute(breakouts_query).df()
    print(df_breakouts.to_string(index=False))

    print("\n" + "="*75)
    print("⚠️ 2026 REGRESSION / SELL-HIGH CANDIDATES (Outperforming Expected Volume)")
    print("="*75)

    regression_query = """
    SELECT 
        player_name,
        position,
        team AS current_team,
        historical_team AS old_team,
        COUNT(*) AS games_played,
        ROUND(AVG(wopr), 2) AS wopr_2025,
        ROUND(AVG(expected_half_ppr_pts), 1) AS expected_fppg,
        ROUND(AVG(actual_half_ppr_pts), 1) AS actual_fppg,
        ROUND(AVG(fpoe), 1) AS fpoe_per_game
    FROM v_master_fantasy_analytics_50
    WHERE season = 2025 AND position IN ('WR', 'TE', 'RB')
    GROUP BY player_name, position, team, historical_team
    HAVING COUNT(*) >= 5 AND AVG(fpoe) >= 2.5
    ORDER BY fpoe_per_game DESC
    LIMIT 10;
    """
    df_regression = con.execute(regression_query).df()
    print(df_regression.to_string(index=False))

    # -------------------------------------------------------------------
    # STEP 3: CONTEXT-ADJUSTED 2026 OFFSEASON TRANSITION PROJECTIONS
    # -------------------------------------------------------------------
    print("\n" + "="*75)
    print("🔄 2026 OFFSEASON TEAM TRANSITIONS (System Volume & Target Competition Adjusted)")
    print("="*75)

    transfers_query = """
    SELECT 
        player_name,
        position,
        old_team,
        new_team,
        target_share_2025,
        proj_2026_target_share,
        new_team_proj_pass_att AS new_team_pass_att_pg,
        proj_2026_weekly_targets,
        proj_2026_xfp_pg
    FROM v_2026_contextual_projections
    WHERE changed_team_flag = 1
    ORDER BY proj_2026_xfp_pg DESC;
    """
    
    try:
        df_transfers = con.execute(transfers_query).df()
        if not df_transfers.empty:
            print(df_transfers.to_string(index=False))
        else:
            print("No team transfers flagged in 2026 context views.")
    except Exception as e:
        print(f"⚠️ Could not query 'v_2026_contextual_projections': {str(e)}")

    con.close()
    print("\n✅ Predictive modeling execution complete.")

if __name__ == "__main__":
    run_predictive_modeling()