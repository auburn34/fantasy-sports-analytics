import duckdb

def generate_production_views():
    con = duckdb.connect("fantasy_analytics.db")
    
    print("Building production analytical views (with Air Yards & aDOT) inside DuckDB...")
    
    con.execute("DROP VIEW IF EXISTS v_player_target_analytics")
    
    create_view_query = """
    CREATE VIEW v_player_target_analytics AS 
    WITH base_games AS (
        SELECT 
            season,
            week,
            player_name,
            position,
            team,
            targets,
            COALESCE(receiving_air_yards, 0) AS air_yards,
            DENSE_RANK() OVER(PARTITION BY season, player_name ORDER BY week) as game_num
        FROM stg_player_stats
        WHERE position IN ('WR', 'TE', 'RB')
          AND team IS NOT NULL
    ),
    team_weekly_totals AS (
        SELECT *,
            SUM(targets) OVER(PARTITION BY season, week, team) AS total_team_targets,
            SUM(air_yards) OVER(PARTITION BY season, week, team) AS total_team_air_yards
        FROM base_games
    ),
    calculated_metrics AS (
        SELECT *,
            -- Target Share %
            CAST(ROUND(CASE 
                WHEN total_team_targets > 0 
                THEN (targets::FLOAT / total_team_targets) * 100
                ELSE 0.0 
            END, 1) AS DECIMAL(5,1)) AS target_share_pct,
            
            -- Air Yard Share %
            CAST(ROUND(CASE 
                WHEN total_team_air_yards > 0 
                THEN (air_yards::FLOAT / total_team_air_yards) * 100
                ELSE 0.0 
            END, 1) AS DECIMAL(5,1)) AS air_yard_share_pct,
            
            -- Average Depth of Target (aDOT)
            CAST(ROUND(CASE 
                WHEN targets > 0 
                THEN (air_yards::FLOAT / targets)
                ELSE 0.0 
            END, 1) AS DECIMAL(5,1)) AS adot,

            -- Rolling 3-week Target Volume
            ROUND(AVG(targets) OVER(
                PARTITION BY season, player_name 
                ORDER BY game_num 
                ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
            ), 1) AS rolling_3wk_targets,

            LAG(targets, 3) OVER(PARTITION BY season, player_name ORDER BY game_num) as targets_4_games_ago
        FROM team_weekly_totals
    ),
    momentum_metrics AS (
        SELECT *,
            CASE 
                WHEN targets_4_games_ago IS NOT NULL THEN ROUND(rolling_3wk_targets - targets_4_games_ago, 1)
                ELSE 0.0 
            END AS target_momentum
        FROM calculated_metrics
    )
    SELECT 
        season,
        week,
        player_name,
        position,
        team,
        targets,
        target_share_pct,
        air_yards,
        air_yard_share_pct,
        adot,
        rolling_3wk_targets,
        target_momentum
    FROM momentum_metrics;
    """
    
    con.execute(create_view_query)
    print("Production view 'v_player_target_analytics' successfully compiled.")
    
    # Preview top Air Yard Share leaders from 2025
    print("\nVerifying Air Yards & aDOT Integration (Top 5 Air Yard Share Leaders in 2025):")
    preview = con.execute("""
        SELECT 
            player_name, 
            position, 
            team, 
            COUNT(*) as games, 
            ROUND(AVG(targets), 1) as avg_targets,
            ROUND(AVG(air_yards), 1) as avg_air_yards,
            ROUND(AVG(air_yard_share_pct), 1) as avg_air_yard_share_pct,
            ROUND(AVG(adot), 1) as avg_adot
        FROM v_player_target_analytics
        WHERE season = 2025 AND targets > 0
        GROUP BY player_name, position, team
        HAVING games >= 6
        ORDER BY avg_air_yard_share_pct DESC
        LIMIT 5;
    """).df()
    
    print(preview.to_string(index=False))
    con.close()

if __name__ == "__main__":
    generate_production_views()