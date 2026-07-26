import duckdb

# Comprehensive 2026 Offseason Transaction Mapping
# Format: (Player Name / Alias, 2026 Team, Acquisition Type)
OFFSEASON_MOVES_2026 = [
    # --- Wide Receivers ---
    ("M.Evans", "SF", "Free Agency"),
    ("Mike Evans", "SF", "Free Agency"),
    ("A.J. Brown", "NE", "Trade from PHI"),
    ("A.Brown", "NE", "Trade from PHI"),
    ("D.J. Moore", "BUF", "Trade from CHI"),
    ("DJ Moore", "BUF", "Trade from CHI"),
    ("D.Moore", "BUF", "Trade from CHI"),
    ("J.Waddle", "DEN", "Trade from MIA"),
    ("Jaylen Waddle", "DEN", "Trade from MIA"),
    ("R.Doubs", "NE", "Free Agency"),
    ("Romeo Doubs", "NE", "Free Agency"),
    ("J.Meyers", "JAX", "Free Agency"),
    ("Jakobi Meyers", "JAX", "Free Agency"),
    ("G.Pickens", "DAL", "Franchise Tag"),
    ("D.Mooney", "FA", "Released by ATL"),

    # --- Running Backs ---
    ("K.Walker", "KC", "Free Agency"),
    ("Kenneth Walker", "KC", "Free Agency"),
    ("D.Montgomery", "HOU", "Trade from DET"),
    ("David Montgomery", "HOU", "Trade from DET"),
    ("B.Hall", "NYJ", "Extension / Franchise Tag"),
    ("R.Dowdle", "PIT", "Free Agency"),
    ("Rico Dowdle", "PIT", "Free Agency"),
    ("J.Williams", "DAL", "Re-Signed"),
    ("Javonte Williams", "DAL", "Re-Signed"),

    # --- Quarterbacks ---
    ("A.Rodgers", "PIT", "Free Agency"),
    ("Aaron Rodgers", "PIT", "Free Agency"),
    ("K.Murray", "MIN", "Free Agency (from ARI)"),
    ("Kyler Murray", "MIN", "Free Agency (from ARI)"),
    ("T.Tagovailoa", "ATL", "Free Agency (from MIA)"),
    ("Tua Tagovailoa", "ATL", "Free Agency (from MIA)"),
    ("K.Cousins", "LV", "Free Agency (from ATL)"),
    ("G.Smith", "NYJ", "Trade from LV"),
    ("Geno Smith", "NYJ", "Trade from LV"),
    ("D.Jones", "IND", "Transition Tag / Extension"),

    # --- Tight Ends ---
    ("K.Pitts", "ATL", "Extension / Franchise Tag"),
    ("D.Knox", "BUF", "Extension"),
]

def sync_rosters():
    con = duckdb.connect("fantasy_analytics.db")
    print("🔄 Updating 2026 Offseason Roster Mappings in DuckDB...")

    # Ensure table structure exists
    con.execute("""
        CREATE TABLE IF NOT EXISTS stg_player_rosters_2026 (
            player_name VARCHAR PRIMARY KEY,
            current_team_2026 VARCHAR,
            acquisition_type VARCHAR
        );
    """)

    # Upsert all roster changes
    for player, team, acq in OFFSEASON_MOVES_2026:
        con.execute("""
            INSERT INTO stg_player_rosters_2026 (player_name, current_team_2026, acquisition_type)
            VALUES (?, ?, ?)
            ON CONFLICT (player_name) DO UPDATE SET 
                current_team_2026 = EXCLUDED.current_team_2026,
                acquisition_type = EXCLUDED.acquisition_type;
        """, [player, team, acq])

    count = con.execute("SELECT COUNT(*) FROM stg_player_rosters_2026").fetchone()[0]
    print(f"✅ Successfully updated {count} player 2026 roster records.")
    con.close()

if __name__ == "__main__":
    sync_rosters()