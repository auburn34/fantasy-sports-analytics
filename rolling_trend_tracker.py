import duckdb

def run_trend_analysis():
    con = duckdb.connect("fantasy_analytics.db")
    
    print("Analyzing 2025 player utilization trends (3-week rolling windows)...")
    
    query = """
    WITH ordered_player_games AS (
        SELECT 
            season,
            week,
            player_name,
            position,
            team,
            targets,
            -- Sequence games consecutively per player to handle bye weeks cleanly
            DENSE_RANK() OVER(PARTITION BY season, player_name ORDER BY week) as game_num
        FROM stg_player_stats
        WHERE season = 2025 
          AND position IN ('WR', 'TE', 'RB')
          AND team IS NOT NULL
    ),
    rolling_averages AS (
        SELECT *,
            -- Calculate the average of the current game and the 2 previous games played
            ROUND(AVG(targets) OVER(
                PARTITION BY season, player_name 
                ORDER BY game_num 
                ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
            ), 1) AS rolling_3wk_targets,
            -- Grab the target count from exactly 3 games ago to calculate the delta
            LAG(targets, 3) OVER(PARTITION BY season, player_name ORDER BY game_num) as targets_4_games_ago
        FROM ordered_player_games
    ),
    trends_calculated AS (
        SELECT *,
            -- Compare current 3-week volume against the game right before this stretch started
            CASE 
                WHEN targets_4_games_ago IS NOT NULL THEN ROUND(rolling_3wk_targets - targets_4_games_ago, 1)
                ELSE 0.0 
            END AS target_momentum
        FROM rolling_averages
    )
    SELECT 
        player_name,
        position,
        team,
        week AS latest_week_analyzed,
        targets AS latest_week_targets,
        rolling_3wk_targets,
        target_momentum
    FROM trends_calculated
    WHERE game_num >= 4  -- Ensure they have enough games to build a rolling baseline
      AND week = (SELECT MAX(week) FROM stg_player_stats WHERE season = 2025)
    ORDER BY target_momentum DESC
    LIMIT 10;
    """
    
    result = con.execute(query).df()
    
    print("\n--- 2025 LATE-SEASON TARGET MOMENTUM SURGE LEADERS ---")
    print(result.to_string(index=False))
    
    con.close()

if __name__ == "__main__":
    run_trend_analysis()