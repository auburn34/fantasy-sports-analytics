import duckdb

def generate_production_views():
    # Connect to our local database file
    con = duckdb.connect("fantasy_analytics.db")
    
    print("Building production analytical views inside DuckDB...")
    
    # We drop the existing view if it exists so we can update it seamlessly
    con.execute("DROP VIEW IF EXISTS v_player_target_analytics")
    
    # Combined production query architecture
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
            DENSE_RANK() OVER(PARTITION BY season, player_name ORDER BY week) as game_num
        FROM stg_player_stats
        WHERE position IN ('WR', 'TE', 'RB')
          AND team IS NOT NULL
    ),
    team_weekly_totals AS (
        SELECT *,
            SUM(targets) OVER(PARTITION BY season, week, team) AS total_team_targets
        FROM base_games
    ),
    calculated_metrics AS (
        SELECT *,
            CASE 
                WHEN total_team_targets > 0 
                THEN ROUND((targets::FLOAT / total_team_targets) * 100, 1)
                ELSE 0.0 
            END AS target_share_pct,
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
        rolling_3wk_targets,
        target_momentum
    FROM momentum_metrics;
    """
    
    # Execute the view creation
    con.execute(create_view_query)
    print("Production view 'v_player_target_analytics' successfully compiled.")
    
    # Verify the view works by pulling a quick preview
    print("\nVerifying view stability (Previewing top 5 high-momentum players from Week 18, 2025):")
    preview = con.execute("""
        SELECT player_name, team, week, targets, target_share_pct, target_momentum
        FROM v_player_target_analytics
        WHERE season = 2025 AND week = 18
        ORDER BY target_momentum DESC
        LIMIT 5;
    """).df()
    
    print(preview.to_string(index=False))
    con.close()

if __name__ == "__main__":
    generate_production_views()