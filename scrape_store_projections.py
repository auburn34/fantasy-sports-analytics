import duckdb
import pandas as pd
import requests
from bs4 import BeautifulSoup

DB_NAME = "fantasy_2026.duckdb"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# Position configurations with specified row limits
POSITIONS = [
    {
        "pos": "QB",
        "cbs_url": "https://www.cbssports.com/fantasy/football/stats/QB/2026/season/projections/nonppr/",
        "fftoday_id": 10,
        "limit": 20,
    },
    {
        "pos": "RB",
        "cbs_url": "https://www.cbssports.com/fantasy/football/stats/RB/2026/season/projections/nonppr/",
        "fftoday_id": 20,
        "limit": 60,
    },
    {
        "pos": "WR",
        "cbs_url": "https://www.cbssports.com/fantasy/football/stats/WR/2026/season/projections/nonppr/",
        "fftoday_id": 30,
        "limit": 60,
    },
    {
        "pos": "TE",
        "cbs_url": "https://www.cbssports.com/fantasy/football/stats/TE/2026/season/projections/nonppr/",
        "fftoday_id": 40,
        "limit": 20,
    },
]


def make_columns_unique(cols):
    """Ensures all column names in a DataFrame are unique to prevent pd.concat errors."""
    seen = {}
    new_cols = []
    for col in cols:
        col_str = str(col).strip()
        if col_str in seen:
            seen[col_str] += 1
            new_cols.append(f"{col_str}_{seen[col_str]}")
        else:
            seen[col_str] = 0
            new_cols.append(col_str)
    return new_cols


def parse_html_tables(html_content):
    """Converts HTML table elements into DataFrames safely without pd.read_html/BeautifulSoup conflicts."""
    soup = BeautifulSoup(html_content, "html.parser")
    tables = soup.find_all("table")
    dfs = []

    for table in tables:
        rows = []
        for tr in table.find_all("tr"):
            cells = [
                td.get_text(strip=True) for td in tr.find_all(["th", "td"])
            ]
            if cells:
                rows.append(cells)

        if len(rows) > 1:
            headers = rows[0]
            data = rows[1:]

            max_len = max(len(r) for r in [headers] + data)
            headers = headers + [
                f"col_{i}" for i in range(len(headers), max_len)
            ]

            cleaned_data = []
            for r in data:
                cleaned_data.append(r + [""] * (max_len - len(r)))

            df = pd.DataFrame(cleaned_data, columns=headers)
            df.columns = make_columns_unique(df.columns)
            dfs.append(df)

    return dfs


def fetch_cbs(url, pos):
    """Scrapes season-long draft projections from CBS Sports."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()

        tables = parse_html_tables(resp.text)
        if not tables:
            return pd.DataFrame()

        df = max(tables, key=len)
        df["Source"] = "CBS Sports"
        df["Position"] = pos

        player_col = [c for c in df.columns if "Player" in str(c)]
        if player_col:
            df["player_name"] = (
                df[player_col[0]]
                .astype(str)
                .str.split("\n")
                .str[0]
                .str.strip()
            )

        return df
    except Exception as e:
        print(f"   [!] CBS Error ({pos}): {e}")
        return pd.DataFrame()


def fetch_fftoday(pos_id, pos):
    """Scrapes season projections from FFToday across paginated tables."""
    all_rows = []

    for page in range(0, 3):
        url = f"https://www.fftoday.com/rankings/playerproj.php?PosID={pos_id}&LeagueID=1&cur_page={page}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()

            tables = parse_html_tables(resp.text)
            target_df = None

            for t in tables:
                col_str = " ".join([str(c) for c in t.columns]).lower()
                row_str = " ".join(t.astype(str).values.flatten()).lower()

                if (
                    "player" in col_str or "player" in row_str or "fpts" in row_str
                ) and len(t) > 5:
                    target_df = t.copy()
                    break

            if target_df is None or target_df.empty:
                break

            # Promote row 0 to header if headers are inside body
            if (
                target_df.iloc[0]
                .astype(str)
                .str.contains("Player|FPts|Tm", case=False)
                .any()
            ):
                target_df.columns = target_df.iloc[0]
                target_df = target_df[1:].reset_index(drop=True)

            target_df.columns = make_columns_unique(target_df.columns)

            player_col = [c for c in target_df.columns if "Player" in str(c)]
            if player_col:
                col = player_col[0]
                target_df = target_df[target_df[col].notna()]
                target_df = target_df[
                    ~target_df[col].str.contains("Player|Sort", na=False)
                ]
                target_df["player_name"] = (
                    target_df[col].astype(str).str.strip()
                )
                target_df["Source"] = "FFToday"
                target_df["Position"] = pos
                all_rows.append(target_df)
            else:
                break

        except Exception as e:
            print(f"   [!] FFToday Error ({pos} page {page}): {e}")
            break

    if all_rows:
        return pd.concat(all_rows, ignore_index=True)
    return pd.DataFrame()


def main():
    print("--- Starting Fantasy Football Scraper (CBS Sports + FFToday) ---\n")
    combined_dfs = []

    for item in POSITIONS:
        pos = item["pos"]
        limit = item["limit"]
        print(f"Scraping position: {pos} (Limit: Top {limit})")

        # Fetch CBS
        print("  Fetching CBS Sports...")
        cbs_df = fetch_cbs(item["cbs_url"], pos)
        if not cbs_df.empty:
            cbs_df = cbs_df.head(limit)
            print(f"    -> CBS Sports {pos}: {len(cbs_df)} rows")
            combined_dfs.append(cbs_df)
        else:
            print(f"    -> CBS Sports {pos}: 0 rows")

        # Fetch FFToday
        print("  Fetching FFToday...")
        ff_df = fetch_fftoday(item["fftoday_id"], pos)
        if not ff_df.empty:
            ff_df = ff_df.head(limit)
            print(f"    -> FFToday {pos}: {len(ff_df)} rows")
            combined_dfs.append(ff_df)
        else:
            print(f"    -> FFToday {pos}: 0 rows")

    if not combined_dfs:
        print("\nNo data scraped. Exiting.")
        return

    print("\n--- Ingesting into DuckDB ---")
    conn = duckdb.connect(DB_NAME)

    for df in combined_dfs:
        source_name = df["Source"].iloc[0].lower().replace(" ", "_")
        pos_name = df["Position"].iloc[0].lower()
        table_name = f"raw_{source_name}_{pos_name}"

        conn.execute(
            f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df"
        )

    print("\n--- DuckDB Position Counts Summary ---")
    summary_df = conn.execute("""
        SELECT 'CBS Sports' as Source, Position, COUNT(*) as player_count 
        FROM (
            SELECT Position FROM raw_cbs_sports_qb
            UNION ALL SELECT Position FROM raw_cbs_sports_rb
            UNION ALL SELECT Position FROM raw_cbs_sports_wr
            UNION ALL SELECT Position FROM raw_cbs_sports_te
        ) GROUP BY Position
        UNION ALL
        SELECT 'FFToday' as Source, Position, COUNT(*) as player_count 
        FROM (
            SELECT Position FROM raw_fftoday_qb
            UNION ALL SELECT Position FROM raw_fftoday_rb
            UNION ALL SELECT Position FROM raw_fftoday_wr
            UNION ALL SELECT Position FROM raw_fftoday_te
        ) GROUP BY Position
        ORDER BY Source, Position;
    """).df()

    print(summary_df.to_string())
    conn.close()
    print(f"\nDatabase successfully updated: '{DB_NAME}'")


if __name__ == "__main__":
    main()