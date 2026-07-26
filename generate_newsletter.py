import os
import sys
import duckdb
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types, errors

# Load environment variables from .env file automatically
load_dotenv(override=True)

def fetch_newsletter_data():
    """Queries DuckDB for the week's key analytical trends."""
    con = duckdb.connect("fantasy_analytics.db", read_only=True)
    
    # 1. Fetch Top Team Transfers / Offseason Volume Shifts
    transfers_query = """
    SELECT 
        player_name, position, old_team, new_team,
        target_share_2025, proj_2026_target_share,
        new_team_proj_pass_att, proj_2026_weekly_targets, proj_2026_xfp_pg
    FROM v_2026_contextual_projections
    WHERE changed_team_flag = 1
    ORDER BY proj_2026_xfp_pg DESC
    LIMIT 5;
    """
    df_transfers = con.execute(transfers_query).df()
    
    # 2. Fetch Buy-Low Candidates (High WOPR / xFP, Underperforming Actuals)
    buy_low_query = """
    SELECT 
        player_name, position, team,
        ROUND(AVG(wopr), 2) AS wopr,
        ROUND(AVG(expected_half_ppr_pts), 1) AS expected_fppg,
        ROUND(AVG(actual_half_ppr_pts), 1) AS actual_fppg,
        ROUND(AVG(fpoe), 1) AS fpoe_per_game
    FROM v_master_fantasy_analytics_50
    WHERE season = 2025 AND position IN ('WR', 'TE')
    GROUP BY player_name, position, team
    HAVING COUNT(*) >= 5 AND AVG(wopr) >= 0.55
    ORDER BY fpoe_per_game ASC
    LIMIT 5;
    """
    df_buy_low = con.execute(buy_low_query).df()

    # 3. Fetch Regression Warnings (High FPOE, Low Volume Baselines)
    regression_query = """
    SELECT 
        player_name, position, team,
        ROUND(AVG(wopr), 2) AS wopr,
        ROUND(AVG(expected_half_ppr_pts), 1) AS expected_fppg,
        ROUND(AVG(actual_half_ppr_pts), 1) AS actual_fppg,
        ROUND(AVG(fpoe), 1) AS fpoe_per_game
    FROM v_master_fantasy_analytics_50
    WHERE season = 2025 AND position IN ('WR', 'RB', 'TE')
    GROUP BY player_name, position, team
    HAVING COUNT(*) >= 5 AND AVG(fpoe) >= 2.5
    ORDER BY fpoe_per_game DESC
    LIMIT 5;
    """
    df_regression = con.execute(regression_query).df()
    
    con.close()
    
    return {
        "transfers": df_transfers.to_dict(orient="records"),
        "buy_lows": df_buy_low.to_dict(orient="records"),
        "regressions": df_regression.to_dict(orient="records")
    }

def generate_newsletter_content(data):
    """Feeds structured DuckDB data into Gemini API to draft newsletter."""
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY environment variable is missing.")
        print("Please ensure your .env file contains: GEMINI_API_KEY='your_key'")
        sys.exit(1)

    # Initialize client explicitly with key string
    client = genai.Client(api_key=api_key)

    system_instruction = """
    You are an elite Fantasy Football Analyst and top 0.1% Yahoo Diamond-tier manager writing an exclusive weekly newsletter.
    Your tone is sharp, data-driven, confident, and conversational with subtle wit. Avoid generic filler.
    Focus heavily on metrics like WOPR (Weighted Opportunity Rating), xFP (Expected Fantasy Points), and context-adjusted target shares.
    
    Structure the newsletter using this template:
    1. Catchy Headline & Brief Introduction (Leveraging your Yahoo Diamond-tier authority)
    2. 🔄 Offseason System Shifts & Volume Transfers (Break down key team relocations)
    3. 🔥 Diamond Buy-Low Breakdown (Uncovering underperforming players with high underlying opportunity)
    4. ⚠️ Regression Red Flags (Exposing players outperforming their underlying volume)
    5. Closing Diamond Takeaway
    """

    prompt = f"""
    Here is this week's underlying analytics payload generated directly from our local DuckDB pipeline:

    ```json
    {json.dumps(data, indent=2)}
    ```

    Please draft the complete issue of the newsletter using these exact numbers and metrics.
    """

    print("🧠 Drafting newsletter with Gemini API...")
    
    # Retry loop to automatically handle transient rate-limit (429) pauses
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                )
            )
            return response.text
        except errors.ClientError as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait_time = 30 * (attempt + 1)
                print(f"⏳ Rate limit pause hit (429). Retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                raise e

def main():
    print("=" * 65)
    print("📰 AUTOMATED NEWSLETTER GENERATION ENGINE")
    print("=" * 65)

    print("\n[1/3] Extracting key metrics from DuckDB...")
    data = fetch_newsletter_data()

    print("\n[2/3] Sending payload to Gemini...")
    newsletter_md = generate_newsletter_content(data)

    output_dir = "newsletters"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/newsletter_{datetime.now().strftime('%Y_%m_%d')}.md"
    
    with open(filename, "w") as f:
        f.write(newsletter_md)

    print(f"\n[3/3] 🎉 Newsletter issue successfully generated and saved to: {filename}")
    print("=" * 65)

if __name__ == "__main__":
    main()