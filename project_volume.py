import duckdb

def build_projected_volume_views():
    con = duckdb.connect("fantasy_analytics.db")
    print("🧠 Compiling 2026 Context-Adjusted Projected Volume Engine (32 Teams)...")

    # 1. Store Team Offense Baselines & System Pass/Run Attempt Expectations
    con.execute("""
        CREATE TABLE IF NOT EXISTS stg_team_schemes_2026 (
            team VARCHAR PRIMARY KEY,
            proj_pass_att_pg FLOAT,
            proj_run_att_pg FLOAT,
            proj_pass_tds_pg FLOAT
        );
    """)

    # Projected 2026 scheme baselines for all 32 NFL teams
    # Format: (Team Abbr, Pass Att/Game, Run Att/Game, Pass TDs/Game)
    ALL_32_TEAM_SCHEMES = [
        ('ARI', 32.5, 27.0, 1.4),
        ('ATL', 34.0, 26.5, 1.6),
        ('BAL', 29.5, 31.0, 1.8),
        ('BUF', 34.0, 26.0, 1.8),
        ('CAR', 33.0, 25.5, 1.3),
        ('CHI', 33.5, 26.0, 1.5),
        ('CIN', 36.0, 23.5, 1.9),
        ('CLE', 32.5, 27.5, 1.3),
        ('DAL', 35.5, 24.5, 1.8),
        ('DEN', 33.0, 27.0, 1.5),
        ('DET', 34.0, 27.0, 1.9),
        ('GB',  33.5, 26.5, 1.7),
        ('HOU', 34.5, 25.5, 1.7),
        ('IND', 31.5, 28.5, 1.5),
        ('JAX', 34.0, 25.0, 1.5),
        ('KC',  35.5, 24.5, 2.1),
        ('LA',  34.5, 25.0, 1.8),
        ('LAC', 31.0, 29.0, 1.5),
        ('LV',  33.5, 25.0, 1.4),
        ('MIA', 33.5, 25.5, 1.6),
        ('MIN', 34.5, 25.0, 1.8),
        ('NE',  33.5, 26.5, 1.4),
        ('NO',  33.0, 26.0, 1.4),
        ('NYG', 33.5, 25.0, 1.3),
        ('NYJ', 33.0, 26.0, 1.5),
        ('PHI', 31.0, 29.5, 1.6),
        ('PIT', 31.5, 28.5, 1.4),
        ('SEA', 33.5, 25.5, 1.5),
        ('SF',  31.5, 29.0, 1.9),
        ('TB',  36.5, 24.0, 1.7),
        ('TEN', 32.0, 27.0, 1.3),
        ('WAS', 33.0, 27.5, 1.6),
    ]

    for team, pass_att, run_att, pass_td in ALL_32_TEAM_SCHEMES:
        con.execute("""
            INSERT INTO stg_team_schemes_2026 (team, proj_pass_att_pg, proj_run_att_pg, proj_pass_tds_pg)
            VALUES (?, ?, ?, ?)
            ON CONFLICT (team) DO UPDATE SET 
                proj_pass_att_pg = EXCLUDED.proj_pass_att_pg,
                proj_run_att_pg = EXCLUDED.proj_run_att_pg,
                proj_pass_tds_pg = EXCLUDED.proj_pass_tds_pg;
        """, [team, pass_att, run_att, pass_td])

    # 2. Build 2026 Contextual Projection View
    con.execute("DROP VIEW IF EXISTS v_2026_contextual_projections")

    con.execute("""
        CREATE VIEW v_2026_contextual_projections AS
        WITH player_2025_baseline AS (
            SELECT 
                player_name,
                position,
                historical_team AS old_team,
                team AS new_team,
                changed_team_flag,
                COUNT(*) as games_played_2025,
                ROUND(AVG(target_share_pct), 1) AS hist_target_share,
                ROUND(AVG(wopr), 2) AS hist_wopr,
                ROUND(AVG(adot), 1) AS hist_adot,
                ROUND(AVG(expected_half_ppr_pts), 1) AS hist_xfp_pg,
                ROUND(AVG(actual_half_ppr_pts), 1) AS hist_fppg
            FROM v_master_fantasy_analytics_50
            WHERE season = 2025
            GROUP BY player_name, position, historical_team, team, changed_team_flag
            HAVING COUNT(*) >= 5
        )
        SELECT 
            b.player_name,
            b.position,
            b.old_team,
            b.new_team,
            b.changed_team_flag,
            b.hist_target_share AS target_share_2025,
            
            -- Target Share Adjustment: Transferred players get adjusted based on new target tree competition
            CAST(ROUND(
                CASE 
                    WHEN b.changed_team_flag = 1 THEN b.hist_target_share * 0.88  -- Adjusts for new environment
                    ELSE b.hist_target_share 
                END, 1) AS DECIMAL(5,1)) AS proj_2026_target_share,

            COALESCE(ts.proj_pass_att_pg, 33.0) AS new_team_proj_pass_att,

            -- Projected Weekly Targets = (Projected Target Share % * New Team Pass Attempts / 100)
            CAST(ROUND(
                ((CASE WHEN b.changed_team_flag = 1 THEN b.hist_target_share * 0.88 ELSE b.hist_target_share END) / 100.0) 
                * COALESCE(ts.proj_pass_att_pg, 33.0), 1) AS DECIMAL(5,1)) AS proj_2026_weekly_targets,

            -- Context-Adjusted Expected Fantasy Points (xFP)
            CAST(ROUND(
                (((CASE WHEN b.changed_team_flag = 1 THEN b.hist_target_share * 0.88 ELSE b.hist_target_share END) / 100.0) 
                 * COALESCE(ts.proj_pass_att_pg, 33.0) * 0.55) + (b.hist_adot * 0.045) + (b.hist_fppg * 0.3), 1) AS DECIMAL(5,1)) AS proj_2026_xfp_pg
        FROM player_2025_baseline b
        LEFT JOIN stg_team_schemes_2026 ts ON b.new_team = ts.team;
    """)

    print("✅ Successfully updated 'stg_team_schemes_2026' with all 32 NFL teams!")
    print("✅ Created 'v_2026_contextual_projections' view!")
    con.close()

if __name__ == "__main__":
    build_projected_volume_views()