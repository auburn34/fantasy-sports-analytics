import duckdb

def run_target_share_analysis():
    # Connect to our local database
    con = duckdb.connect("fantasy_analytics.db")
    
    print("Calculating true weekly target shares for the 2025 season...")
    
    # This query calculates individual targets vs team total weekly targets
    query = """
    WITH weekly_team_totals AS (
        SELECT 
            season,
            week,
            player_name,
            position,
            team AS player_team,
            targets AS player_targets,
            -- Window function to sum all targets for a team in a specific week
            SUM(targets) OVER(PARTITION BY season, week, team) AS total_team_targets
        FROM stg_player_stats
        WHERE season = 2025 
          AND position IN ('WR', 'TE', 'RB')
          AND team IS NOT NULL
    ),
    target_share_calc AS (
        SELECT *,
            CASE 
                WHEN total_team_targets > 0 
                THEN ROUND((player_targets::FLOAT / total_team_targets) * 100, 1)
                ELSE 0.0 
            END AS target_share_pct
        FROM weekly_team_totals
    )
    SELECT 
        player_name,
        position,
        player_team,
        COUNT(*) AS weeks_played,
        ROUND(AVG(player_targets), 1) AS avg_targets_per_game,
        ROUND(AVG(target_share_pct), 1) AS avg_target_share_pct,
        MAX(target_share_pct) AS peak_single_week_share
    FROM target_share_calc
    WHERE player_targets > 0
    GROUP BY player_name, position, player_team
    HAVING weeks_played >= 4  -- Filter out small sample sizes
    ORDER BY avg_target_share_pct DESC
    LIMIT 20;
    """
    
    result = con.execute(query).df()
    
    print("\n--- 2025 TOP 10 TARGET SHARE LEADERS ---")
    print(result.to_string(index=False))
    
    con.close()

if __name__ == "__main__":
    run_target_share_analysis()