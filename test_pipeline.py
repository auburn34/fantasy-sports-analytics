import nflreadpy as nfl
import duckdb

print("Fetching weekly data summary using nflreadpy...")
# Load 2025 player stats
df = nfl.load_player_stats([2025])

# Using COUNT(*) instead of summing a team column to get total weeks played
result = duckdb.query("""
    SELECT 
        player_name, 
        position, 
        COUNT(*) as total_weeks, 
        SUM(targets) as total_targets
    FROM df
    WHERE position IN ('WR', 'TE', 'RB')
    GROUP BY player_name, position
    ORDER BY total_targets DESC
    LIMIT 5
""").df()

print("\nTop 5 Targets in 2025:")
print(result)