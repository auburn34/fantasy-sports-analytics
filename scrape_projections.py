import json
import time
import pandas as pd
import requests

# Standard browser User-Agent header
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

# ESPN Slot / Position ID Map
ESPN_POS_MAP = {1: "QB", 2: "RB", 3: "WR", 4: "TE", 16: "D/ST", 17: "K"}


def scrape_fantasypros(pos="qb"):
    """Scrapes season-long draft projections from FantasyPros."""
    url = f"https://www.fantasypros.com/nfl/projections/{pos.lower()}.php?week=draft"

    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            tables = pd.read_html(res.text)
            df = tables[0]

            # Flatten multi-index column headers
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [
                    (
                        f"{col[0]}_{col[1]}"
                        if "Unnamed" not in col[0]
                        else col[1]
                    )
                    for col in df.columns
                ]

            df["Source"] = "FantasyPros"
            df["Position"] = pos.upper()
            return df
        else:
            print(
                f"  [FantasyPros] Failed to fetch {pos.upper()} (Status Code: {res.status_code})"
            )
            return pd.DataFrame()
    except Exception as e:
        print(f"  [FantasyPros] Error scraping {pos.upper()}: {e}")
        return pd.DataFrame()


def scrape_cbs(pos="qb", scoring="ppr"):
    """Scrapes season-long draft projections from CBS Sports."""
    pos_code = pos.upper()
    url = f"https://www.cbssports.com/fantasy/football/stats/{pos_code}/2026/season/projections/{scoring}/"

    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            tables = pd.read_html(res.text)
            df = tables[0]

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [
                    (
                        f"{col[0]}_{col[1]}"
                        if "Unnamed" not in col[0]
                        else col[1]
                    )
                    for col in df.columns
                ]

            df["Source"] = "CBS Sports"
            df["Position"] = pos_code
            return df
        else:
            print(
                f"  [CBS Sports] Failed to fetch {pos_code} (Status Code: {res.status_code})"
            )
            return pd.DataFrame()
    except Exception as e:
        print(f"  [CBS Sports] Error scraping {pos_code}: {e}")
        return pd.DataFrame()


def scrape_espn(pos="qb", limit=50):
    """Fetches season-long projections directly from ESPN's public API."""
    pos_upper = pos.upper()
    target_pos_id = [k for k, v in ESPN_POS_MAP.items() if v == pos_upper]

    if not target_pos_id:
        print(f"  [ESPN] Unsupported position: {pos}")
        return pd.DataFrame()

    pos_id = target_pos_id[0]

    # ESPN Public API Endpoint
    url = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2026/players?scoringPeriodId=0&view=players_wl"

    # ESPN Header Filter to request projections for specific position
    filter_header = {
        "players": {
            "filterSlotIds": {"value": [pos_id]},
            "limit": limit,
            "sortDraftRanks": {
                "sortPriority": 100,
                "sortAsc": True,
                "value": "STANDARD",
            },
        }
    }

    espn_headers = HEADERS.copy()
    espn_headers["X-Fantasy-Filter"] = json.dumps(filter_header)

    try:
        res = requests.get(url, headers=espn_headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            rows = []

            for player in data:
                full_name = player.get("fullName", "")

                # Extract projected total points for the 2026 season
                proj_pts = None
                stats = player.get("stats", [])
                for stat in stats:
                    # statSourceId == 1 corresponds to projected stats, seasonId == 2026
                    if (
                        stat.get("statSourceId") == 1
                        and stat.get("seasonId") == 2026
                    ):
                        proj_pts = stat.get("appliedTotal", 0.0)
                        break

                rows.append(
                    {
                        "Player": full_name,
                        "Position": pos_upper,
                        "ESPN_Projected_FPTS": proj_pts,
                        "Source": "ESPN",
                    }
                )

            df = pd.DataFrame(rows)
            return df
        else:
            print(
                f"  [ESPN] Failed to fetch {pos_upper} (Status Code: {res.status_code})"
            )
            return pd.DataFrame()
    except Exception as e:
        print(f"  [ESPN] Error fetching {pos_upper}: {e}")
        return pd.DataFrame()


def main():
    positions = ["qb", "rb", "wr", "te"]
    all_frames = []

    print("--- Starting 2026 Multi-Source Fantasy Football Scraper ---")

    for pos in positions:
        print(f"\nScraping position: {pos.upper()}")

        # 1. FantasyPros
        print("  Fetching FantasyPros...")
        fp_df = scrape_fantasypros(pos)
        if not fp_df.empty:
            all_frames.append(fp_df)

        # 2. CBS Sports
        print("  Fetching CBS Sports...")
        cbs_df = scrape_cbs(pos)
        if not cbs_df.empty:
            all_frames.append(cbs_df)

        # 3. ESPN API
        print("  Fetching ESPN...")
        espn_df = scrape_espn(pos, limit=50)
        if not espn_df.empty:
            all_frames.append(espn_df)

        time.sleep(1)

    # Combine and save output
    if all_frames:
        combined_df = pd.concat(all_frames, ignore_index=True)
        output_filename = "2026_fantasy_projections_raw.csv"
        combined_df.to_csv(output_filename, index=False)

        print(f"\n Success! Saved aggregated data to '{output_filename}'")
        print(f"Total rows collected: {len(combined_df)}")
    else:
        print("\n No data was retrieved.")


if __name__ == "__main__":
    main()