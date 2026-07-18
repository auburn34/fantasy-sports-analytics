import duckdb
import nflreadpy as nfl

def load_history():
    seasons = [2021, 2022, 2023, 2024, 2025]
    print(f"Fetching raw weekly stats for seasons: {seasons}...")
    
    # Extract data from the live API
    raw_df = nfl.load_player_stats(seasons)
    
    # Connect to our persistent local database
    con = duckdb.connect("fantasy_analytics.db")
    
    print("Clearing out any previous staging data to avoid duplicates...")
    con.execute("TRUNCATE TABLE stg_player_stats")
    
    print("Loading historical data into 'stg_player_stats'...")
    # Insert the Polars DataFrame directly into our DuckDB table
    con.execute("INSERT INTO stg_player_stats SELECT * FROM raw_df")
    
    # Verify row counts and available seasons
    metrics = con.execute("""
        SELECT 
            season, 
            COUNT(*) as total_rows,
            COUNT(DISTINCT player_id) as unique_players
        FROM stg_player_stats 
        GROUP BY season
        ORDER BY season DESC
    """).df()
    
    print("\nData Load Successful! Historical Summary:")
    print(metrics)
    
    con.close()

if __name__ == "__main__":
    load_history()