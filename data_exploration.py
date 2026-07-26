import duckdb

con = duckdb.connect("fantasy_analytics.db")

# 1. Inspect table structure / columns
# Fetch column names directly as a list

print("--- COLUMN LIST & TYPES ---")
columns = con.execute("DESCRIBE stg_player_stats").df()['column_name'].tolist()

print(f"--- TOTAL COLUMNS: {len(columns)} ---")
for i, col in enumerate(columns, 1):
    print(f"{i:2d}. {col}")


# 2. Check total row count by position
print("\n--- Show entire table ---")
print(con.execute("""
    SELECT * 
    FROM stg_player_stats 
    LIMIT 100
""").df())

# 2. Check total row count by position
print("\n--- ROW COUNT BY POSITION ---")
print(con.execute("""
    SELECT position, COUNT(*) as rows 
    FROM stg_player_stats 
    GROUP BY position 
    ORDER BY rows DESC
""").df())

# 3. Pull top passing performances in 2025
print("\n--- TOP PASSING GAMES 2025 ---")
print(con.execute("""
    SELECT player_name, team, week, passing_yards, passing_tds 
    FROM stg_player_stats 
    WHERE season = 2025 
    ORDER BY passing_yards DESC 
    LIMIT 5
""").df())

con.close()