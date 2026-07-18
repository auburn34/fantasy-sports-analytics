import duckdb
import nflreadpy as nfl

def init_database():
    print("Connecting to local DuckDB database (creating if it doesn't exist)...")
    # This creates a persistent file named fantasy_analytics.db in your project folder
    con = duckdb.connect("fantasy_analytics.db")
    
    print("Fetching 2025 raw data to initialize schema structure...")
    # Grab a sample dataset to map out our columns dynamically
    raw_df = nfl.load_player_stats([2025])
    
    print("Creating staging table 'stg_player_stats'...")
    # DuckDB can create a table directly from a Polars dataframe structure
    con.execute("CREATE TABLE IF NOT EXISTS stg_player_stats AS SELECT * FROM raw_df WHERE 1=0")
    
    # Let's verify the table structure exists
    tables = con.execute("SHOW TABLES").fetchall()
    print(f"\nDatabase Initialization Successful! Active tables: {tables}")
    
    con.close()

if __name__ == "__main__":
    init_database()