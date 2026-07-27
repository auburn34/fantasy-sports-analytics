import os
import json
import logging
from typing import List, Dict, Optional
import pandas as pd
import requests

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class FFAProjectionScraper:
    """
    Module to fetch and aggregate seasonal projection data by position 
    from consensus projection feeds (Fantasy Football Analytics vector).
    """

    def __init__(self, season: int = 2026):
        self.season = season
        self.positions = ["QB", "RB", "WR", "TE", "DST", "K"]
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }

    def fetch_direct_csv(self, download_url: str) -> Optional[pd.DataFrame]:
        """
        Directly ingests a CSV download URL captured from network traffic 
        in the dashboard console via pandas.
        """
        try:
            logger.info("Fetching projection dataset directly from endpoint...")
            df = pd.read_csv(download_url)
            logger.info(f"Successfully loaded {len(df)} records.")
            return df
        except Exception as e:
            logger.error(f"Failed to fetch CSV from {download_url}: {e}")
            return None

    def fetch_position_projections(self, position: str, endpoint_url: str) -> pd.DataFrame:
        """
        Queries raw positional data endpoints and structures response data.
        """
        if position.upper() not in self.positions:
            raise ValueError(f"Invalid position: {position}. Must be one of {self.positions}")

        logger.info(f"Scraping {self.season} projections for position: {position}")

        params = {
            "season": self.season,
            "position": position.upper(),
            "format": "json"
        }

        try:
            response = requests.get(endpoint_url, headers=self.headers, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()
            df = pd.DataFrame(data)
            df["position"] = position.upper()
            df["season"] = self.season
            return df

        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred while fetching {position}: {http_err}")
        except Exception as err:
            logger.error(f"An error occurred while fetching {position}: {err}")

        return pd.DataFrame()

    def scrape_all_positions(self, endpoint_url: str) -> pd.DataFrame:
        """
        Loops through all skill positions and returns a consolidated DataFrame.
        """
        all_projections = []
        for pos in ["QB", "RB", "WR", "TE"]:
            df_pos = self.fetch_position_projections(pos, endpoint_url)
            if not df_pos.empty:
                all_projections.append(df_pos)

        if all_projections:
            consolidated = pd.concat(all_projections, ignore_index=True)
            return self._clean_and_standardize(consolidated)
        
        return pd.DataFrame()

    def _clean_and_standardize(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardizes column names and formats metric types for analytical pipelines.
        """
        df.columns = [col.lower().replace(" ", "_").replace(".", "_") for col in df.columns]

        numeric_cols = [c for c in df.columns if c not in ["player", "player_name", "team", "position"]]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        return df


if __name__ == "__main__":
    scraper = FFAProjectionScraper(season=2026)
    print("Scraper class loaded successfully.")