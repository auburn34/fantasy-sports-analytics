import duckdb

def create_50_analytics_view():
    con = duckdb.connect("fantasy_analytics.db")
    print("Compiling 50 Predictive & Contextual Fantasy Analytics Metrics into DuckDB View...")

    con.execute("DROP VIEW IF EXISTS v_master_fantasy_analytics_50")

    query = """
    CREATE VIEW v_master_fantasy_analytics_50 AS 
    WITH raw_player_data AS (
        SELECT 
            season,
            week,
            player_name,
            position,
            team,
            -- Core Raw Volume
            COALESCE(targets, 0) AS targets,
            COALESCE(receptions, 0) AS receptions,
            COALESCE(carries, 0) AS carries,
            (COALESCE(carries, 0) + COALESCE(receptions, 0)) AS total_touches,
            
            -- Core Yardage
            COALESCE(receiving_yards, 0) AS receiving_yards,
            COALESCE(rushing_yards, 0) AS rushing_yards,
            (COALESCE(receiving_yards, 0) + COALESCE(rushing_yards, 0)) AS total_yards,
            COALESCE(receiving_yards_after_catch, 0) AS yac_yards,
            COALESCE(receiving_first_downs, 0) + COALESCE(rushing_first_downs, 0) AS first_downs_earned,
            
            -- TDs & Indicators
            COALESCE(receiving_tds, 0) AS receiving_tds,
            COALESCE(rushing_tds, 0) AS rushing_tds,
            (COALESCE(receiving_tds, 0) + COALESCE(rushing_tds, 0)) AS total_tds,
            COALESCE(receiving_air_yards, 0) AS air_yards,
            
            -- Red Zone Volume Proxies
            COALESCE(receiving_tds, 0) AS redzone_targets,
            COALESCE(rushing_tds, 0) AS redzone_carries,
            
            -- Sequence game counts per player
            DENSE_RANK() OVER(PARTITION BY season, player_name ORDER BY week) as season_game_num,
            DENSE_RANK() OVER(PARTITION BY player_name ORDER BY season, week) as career_game_num,
            
            -- Track prior team
            LAG(team, 1) OVER(PARTITION BY player_name ORDER BY season, week) as prev_team
        FROM stg_player_stats
        WHERE position IN ('WR', 'TE', 'RB') AND team IS NOT NULL
    ),
    team_weekly_totals AS (
        SELECT *,
            SUM(targets) OVER(PARTITION BY season, week, team) AS total_team_targets,
            SUM(carries) OVER(PARTITION BY season, week, team) AS total_team_carries,
            SUM(total_touches) OVER(PARTITION BY season, week, team) AS total_team_touches,
            SUM(air_yards) OVER(PARTITION BY season, week, team) AS total_team_air_yards,
            (SUM(targets) OVER(PARTITION BY season, week, team) + SUM(carries) OVER(PARTITION BY season, week, team)) AS total_team_play_volume
        FROM raw_player_data
    ),
    calculated_metrics AS (
        SELECT *,
            -- 1. Volume Market Shares
            CAST(ROUND(CASE WHEN total_team_targets > 0 THEN (targets::FLOAT / total_team_targets) * 100 ELSE 0.0 END, 1) AS DECIMAL(5,1)) AS target_share_pct,
            CAST(ROUND(CASE WHEN total_team_carries > 0 THEN (carries::FLOAT / total_team_carries) * 100 ELSE 0.0 END, 1) AS DECIMAL(5,1)) AS carry_share_pct,
            CAST(ROUND(CASE WHEN total_team_touches > 0 THEN (total_touches::FLOAT / total_team_touches) * 100 ELSE 0.0 END, 1) AS DECIMAL(5,1)) AS touch_share_pct,
            
            -- 2. Air Yards & Advanced Opportunities
            CAST(ROUND(CASE WHEN total_team_air_yards > 0 THEN (air_yards::FLOAT / total_team_air_yards) * 100 ELSE 0.0 END, 1) AS DECIMAL(5,1)) AS air_yard_share_pct,
            CAST(ROUND((1.5 * (CASE WHEN total_team_targets > 0 THEN targets::FLOAT / total_team_targets ELSE 0.0 END)) + 
                       (0.7 * (CASE WHEN total_team_air_yards > 0 THEN air_yards::FLOAT / total_team_air_yards ELSE 0.0 END)), 2) AS DECIMAL(5,2)) AS wopr,
            CAST(ROUND(CASE WHEN air_yards > 0 THEN (receiving_yards::FLOAT / air_yards) ELSE 0.0 END, 2) AS DECIMAL(5,2)) AS racr,

            -- 3. Red Zone Aggregates
            (redzone_targets + redzone_carries) AS redzone_touches,

            -- 4. Efficiency & Per-Play Metrics
            CAST(ROUND(CASE WHEN targets > 0 THEN (air_yards::FLOAT / targets) ELSE 0.0 END, 1) AS DECIMAL(5,1)) AS adot,
            CAST(ROUND(CASE WHEN targets > 0 THEN (receptions::FLOAT / targets) * 100 ELSE 0.0 END, 1) AS DECIMAL(5,1)) AS catch_rate_pct,
            CAST(ROUND(CASE WHEN receptions > 0 THEN (yac_yards::FLOAT / receptions) ELSE 0.0 END, 1) AS DECIMAL(5,1)) AS yac_per_reception,
            CAST(ROUND(CASE WHEN targets > 0 THEN (receiving_yards::FLOAT / targets) ELSE 0.0 END, 1) AS DECIMAL(5,1)) AS yards_per_target,
            CAST(ROUND(CASE WHEN carries > 0 THEN (rushing_yards::FLOAT / carries) ELSE 0.0 END, 1) AS DECIMAL(5,1)) AS yards_per_carry,
            CAST(ROUND(CASE WHEN total_touches > 0 THEN (total_yards::FLOAT / total_touches) ELSE 0.0 END, 1) AS DECIMAL(5,1)) AS yards_per_touch,
            CAST(ROUND(CASE WHEN total_touches > 0 THEN (first_downs_earned::FLOAT / total_touches) * 100 ELSE 0.0 END, 1) AS DECIMAL(5,1)) AS first_down_rate_pct,
            CAST(ROUND(CASE WHEN total_touches > 0 THEN (total_tds::FLOAT / total_touches) * 100 ELSE 0.0 END, 1) AS DECIMAL(5,1)) AS td_per_touch_pct,

            -- 5. Fantasy Point Scoring Formats
            CAST(ROUND((total_yards * 0.1) + (total_tds * 6.0), 1) AS DECIMAL(5,1)) AS actual_std_pts,
            CAST(ROUND((receptions * 0.5) + (total_yards * 0.1) + (total_tds * 6.0), 1) AS DECIMAL(5,1)) AS actual_half_ppr_pts,
            CAST(ROUND((receptions * 1.0) + (total_yards * 0.1) + (total_tds * 6.0), 1) AS DECIMAL(5,1)) AS actual_ppr_pts,
            
            -- 6. Predictive xFP & Luck Regression
            CAST(ROUND((carries * 0.6) + (targets * 0.55) + (air_yards * 0.045) + (receptions * 0.5) + (total_tds * 1.2), 1) AS DECIMAL(5,1)) AS expected_half_ppr_pts,
            CAST(ROUND((carries * 0.035) + (targets * 0.04) + (total_tds * 0.15), 2) AS DECIMAL(5,2)) AS expected_tds,

            -- 7. Team Context & Volume Profiling
            total_team_targets AS team_pass_volume,
            total_team_carries AS team_run_volume,
            CAST(ROUND(CASE WHEN total_team_play_volume > 0 THEN (total_team_targets::FLOAT / total_team_play_volume) * 100 ELSE 0.0 END, 1) AS DECIMAL(5,1)) AS team_pass_ratio_pct,

            -- 8. Rolling Windows
            ROUND(AVG(targets) OVER(PARTITION BY season, player_name ORDER BY season_game_num ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 1) AS rolling_3wk_targets,
            LAG(targets, 3) OVER(PARTITION BY season, player_name ORDER BY season_game_num) as targets_4_games_ago,
            ROUND(AVG((receptions * 0.5) + (total_yards * 0.1) + (total_tds * 6.0)) OVER(PARTITION BY season, player_name ORDER BY season_game_num ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 1) AS rolling_3wk_fppg,
            LAG((receptions * 0.5) + (total_yards * 0.1) + (total_tds * 6.0), 3) OVER(PARTITION BY season, player_name ORDER BY season_game_num) as fppg_4_games_ago
        FROM team_weekly_totals
    ),
    final_output AS (
        SELECT *,
            -- Derived Deltas & Points Over Expectation
            CASE WHEN targets_4_games_ago IS NOT NULL THEN ROUND(rolling_3wk_targets - targets_4_games_ago, 1) ELSE 0.0 END AS target_momentum,
            CASE WHEN fppg_4_games_ago IS NOT NULL THEN ROUND(rolling_3wk_fppg - fppg_4_games_ago, 1) ELSE 0.0 END AS fppg_momentum,
            CAST(ROUND(actual_half_ppr_pts - expected_half_ppr_pts, 1) AS DECIMAL(5,1)) AS fpoe,
            CAST(ROUND(CASE WHEN total_touches > 0 THEN (actual_half_ppr_pts - expected_half_ppr_pts) / total_touches ELSE 0.0 END, 2) AS DECIMAL(5,2)) AS fpoe_per_touch
        FROM calculated_metrics
    )
    SELECT 
        f.season, 
        f.week, 
        f.player_name, 
        f.position, 
        f.team AS historical_team,
        COALESCE(r.current_team_2026, f.team) AS team,
        f.prev_team, 
        CASE WHEN r.current_team_2026 IS NOT NULL AND r.current_team_2026 != f.team THEN 1 ELSE 0 END AS changed_team_flag,
        f.season_game_num AS games_played_season, 
        f.career_game_num,
        
        -- Volume & Touches
        f.targets, f.receptions, f.carries, f.total_touches, f.target_share_pct, f.carry_share_pct, f.touch_share_pct,
        
        -- Air Yards & Market Opportunity
        f.air_yards, f.air_yard_share_pct, f.adot, f.wopr, f.racr,
        
        -- Yardage & Production
        f.receiving_yards, f.rushing_yards, f.total_yards, f.yac_yards, f.yac_per_reception, f.first_downs_earned,
        
        -- Red Zone Opportunities
        f.receiving_tds, f.rushing_tds, f.total_tds, f.redzone_targets, f.redzone_carries, f.redzone_touches,
        
        -- Efficiency & Per-Play Metrics
        f.catch_rate_pct, f.yards_per_target, f.yards_per_carry, f.yards_per_touch, f.first_down_rate_pct, f.td_per_touch_pct,
        
        -- Fantasy Point Outputs
        f.actual_std_pts, f.actual_half_ppr_pts AS fppg_half_ppr, f.actual_half_ppr_pts, f.actual_ppr_pts,
        
        -- Predictive Models & Luck Regression
        f.expected_half_ppr_pts, f.expected_tds, f.fpoe, f.fpoe_per_touch,
        
        -- Trajectory, Context & Team Profiling
        f.rolling_3wk_targets, f.target_momentum, f.rolling_3wk_fppg, f.fppg_momentum,
        f.team_pass_volume, f.team_run_volume
    FROM final_output f
    LEFT JOIN stg_player_rosters_2026 r ON f.player_name = r.player_name;
    """

    con.execute(query)
    print("✅ Production View 'v_master_fantasy_analytics_50' created with 50 Predictive Metrics!")

    # Verify View
    print("\n--- PREVIEW: TOP 5 WOPR LEADERS IN DATASET ---")
    preview = con.execute("""
        SELECT 
            player_name, position, team, historical_team,
            COUNT(*) as games,
            ROUND(AVG(wopr), 2) as avg_wopr,
            ROUND(AVG(target_share_pct), 1) as avg_target_share,
            ROUND(AVG(expected_half_ppr_pts), 1) as avg_xfp
        FROM v_master_fantasy_analytics_50
        WHERE season = 2025 AND targets > 0
        GROUP BY player_name, position, team, historical_team
        HAVING games >= 6
        ORDER BY avg_wopr DESC
        LIMIT 5;
    """).df()
    print(preview.to_string(index=False))

    con.close()

if __name__ == "__main__":
    create_50_analytics_view()