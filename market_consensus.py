import json
import urllib.request
import re
import pandas as pd

def clean_name_key(full_name: str) -> str:
    """Creates a normalized string for matching (e.g., 'J. Smith-Njigba' -> 'jsmithnjigba')."""
    if not full_name:
        return ""
    # Strip dots, spaces, hyphens, apostrophes
    cleaned = re.sub(r"[^a-zA-Z]", "", full_name).lower()
    # If formatted as 'J. Smith', reduce first name to initial
    return cleaned

def get_sleeper_market_adp() -> pd.DataFrame:
    """Fetches real-time Sleeper market rankings and creates robust name keys."""
    print("📡 Querying live market consensus from Sleeper API...")
    url = "https://api.sleeper.app/v1/players/nfl"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        print(f"⚠️ Failed to fetch Sleeper market data: {e}")
        return pd.DataFrame()
    
    players = []
    for player_id, info in data.items():
        if info.get('position') in ['QB', 'RB', 'WR', 'TE'] and info.get('active'):
            first_name = info.get('first_name', '')
            last_name = info.get('last_name', '')
            full_name = f"{first_name} {last_name}".strip()
            
            # Key for matching: 'j' + 'smithnjigba'
            first_initial = first_name[0].lower() if first_name else ""
            clean_last = re.sub(r"[^a-zA-Z]", "", last_name).lower()
            match_key = f"{first_initial}{clean_last}"
            
            # Sleeper search_rank indicates market popularity
            search_rank = info.get('search_rank', 999)
            
            players.append({
                'sleeper_id': player_id,
                'full_name': full_name,
                'match_key': match_key,
                'position': info.get('position'),
                'team': info.get('team'),
                'market_adp': float(search_rank) if search_rank else 250.0
            })
            
    df_market = pd.DataFrame(players)
    if df_market.empty:
        return df_market

    # Sort by market rank and deduce positional market rank
    df_market = df_market.sort_values('market_adp').reset_index(drop=True)
    df_market['market_pos_rank'] = df_market.groupby('position').cumcount() + 1
    
    return df_market