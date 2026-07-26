import duckdb

def init_database():
    con = duckdb.connect("fantasy_analytics.db")
    print("Initializing DuckDB Schema Structures...")
    
    # 1. Base historical staging table
    con.execute("""
        CREATE TABLE IF NOT EXISTS stg_player_stats (
            season INTEGER,
            week INTEGER,
            player_name VARCHAR,
            position VARCHAR,
            team VARCHAR,
            targets INTEGER,
            receptions INTEGER,
            carries INTEGER,
            receiving_yards FLOAT,
            rushing_yards FLOAT,
            receiving_tds INTEGER,
            rushing_tds INTEGER,
            receiving_air_yards FLOAT,
            receiving_yards_after_catch FLOAT,
            receiving_first_downs INTEGER,
            rushing_first_downs INTEGER
        );
    """)

    # 2. 2026 Current Offseason Team Mapping Table
    con.execute("""
        CREATE TABLE IF NOT EXISTS stg_player_rosters_2026 (
            player_name VARCHAR PRIMARY KEY,
            current_team_2026 VARCHAR,
            acquisition_type VARCHAR
        );
    """)

    # Populate/Update known 2026 key player movements
    roster_updates = [
        ('M.Evans', 'SF', 'Free Agency'),
        # Add any other major 2026 player transfers here as free agency / trades unfold
    ]

    for player, team, acq in roster_updates:
        con.execute("""
            INSERT INTO stg_player_rosters_2026 (player_name, current_team_2026, acquisition_type)
            VALUES (?, ?, ?)
            ON CONFLICT (player_name) DO UPDATE SET 
                current_team_2026 = EXCLUDED.current_team_2026,
                acquisition_type = EXCLUDED.acquisition_type;
        """, [player, team, acq])

    print("✅ Database schemas and 2026 Roster Mappings initialized successfully.")
    con.close()

if __name__ == "__main__":
    init_database()