import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

# -------------------------------------------------------------------
# PAGE CONFIGURATION & DIAMOND BRANDING
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Analytics Command Center | Yahoo Diamond Tier",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Brand Presence
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #64748B;
        margin-bottom: 20px;
    }
    .diamond-badge {
        background-color: #0F172A;
        color: #38BDF8;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# DATABASE CONNECTION
# -------------------------------------------------------------------
@st.cache_resource
def get_db_connection():
    # Connect read-only to prevent DB locking while background pipeline runs
    return duckdb.connect("fantasy_analytics.db", read_only=True)

try:
    con = get_db_connection()
except Exception as e:
    st.error(f"❌ Could not connect to DuckDB database: {e}")
    st.stop()

# -------------------------------------------------------------------
# HEADER & SIDEBAR CONTROLS
# -------------------------------------------------------------------
col_title, col_badge = st.columns([4, 1])
with col_title:
    st.markdown('<div class="main-header">🏈 Fantasy Analytics Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Automated Insights & Context-Adjusted Projections</div>', unsafe_allow_html=True)
with col_badge:
    st.markdown('<br><span class="diamond-badge">💎 YAHOO DIAMOND TIER</span>', unsafe_allow_html=True)

st.sidebar.header("🎯 Filter Controls")

# Sidebar Filters
position_filter = st.sidebar.multiselect(
    "Position",
    options=["WR", "RB", "TE"],
    default=["WR", "RB", "TE"]
)

min_games = st.sidebar.slider("Minimum Games Played (2025)", 1, 17, 5)

wopr_min = st.sidebar.slider("Minimum WOPR Score", 0.0, 1.0, 0.30, step=0.05)

# -------------------------------------------------------------------
# DASHBOARD TABS
# -------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "🔄 2026 Team Transitions", 
    "📈 Buy-Low / Regression Scatter", 
    "📊 Master 50-Metric Explorer"
])

# -------------------------------------------------------------------
# TAB 1: 2026 TEAM TRANSITIONS & CONTEXT ADJUSTMENTS
# -------------------------------------------------------------------
with tab1:
    st.subheader("Offseason Team Transitions & Scheme Volume Adjustments")
    st.caption("Evaluates volume shifts for transferred players (e.g., Mike Evans to SF, AJ Brown to NE).")

    transfers_query = f"""
    SELECT 
        player_name AS "Player",
        position AS "Pos",
        old_team AS "Old Team",
        new_team AS "New Team",
        target_share_2025 AS "2025 Share (%)",
        proj_2026_target_share AS "2026 Proj Share (%)",
        new_team_proj_pass_att AS "New Team Pass Att/G",
        proj_2026_weekly_targets AS "Proj Targets/G",
        proj_2026_xfp_pg AS "Proj xFP/G"
    FROM v_2026_contextual_projections
    WHERE changed_team_flag = 1 
      AND position IN ({','.join([f"'{p}'" for p in position_filter])})
    ORDER BY proj_2026_xfp_pg DESC;
    """
    
    df_transfers = con.execute(transfers_query).df()
    
    if not df_transfers.empty:
        st.dataframe(df_transfers, use_container_width=True, hide_index=True)
        
        # Bar Chart of Projected Weekly Targets
        fig_transfers = px.bar(
            df_transfers,
            x="Player",
            y="Proj Targets/G",
            color="New Team",
            text="Proj Targets/G",
            title="Projected Weekly Target Volume in New Offenses",
            hover_data=["Old Team", "2026 Proj Share (%)", "Proj xFP/G"]
        )
        fig_transfers.update_traces(textposition="outside")
        st.plotly_chart(fig_transfers, use_container_width=True)
    else:
        st.info("No team transfers match the current filter selection.")

# -------------------------------------------------------------------
# TAB 2: OPPORTUNITY VS OUTCOME (WOPR vs FPOE Scatter)
# -------------------------------------------------------------------
with tab2:
    st.subheader("Opportunity (Expected xFP) vs Actual Scoring (FPOE)")
    st.caption("Players in the top-left are high-volume buy-low targets. Top-right are elite performers.")

    scatter_query = f"""
    SELECT 
        player_name,
        position,
        team,
        ROUND(AVG(wopr), 2) AS avg_wopr,
        ROUND(AVG(expected_half_ppr_pts), 1) AS expected_fppg,
        ROUND(AVG(actual_half_ppr_pts), 1) AS actual_fppg,
        ROUND(AVG(fpoe), 1) AS fpoe_per_game,
        COUNT(*) AS gms
    FROM v_master_fantasy_analytics_50
    WHERE season = 2025 
      AND position IN ({','.join([f"'{p}'" for p in position_filter])})
    GROUP BY player_name, position, team
    HAVING COUNT(*) >= {min_games} AND AVG(wopr) >= {wopr_min};
    """
    
    df_scatter = con.execute(scatter_query).df()

    if not df_scatter.empty:
        fig_scatter = px.scatter(
            df_scatter,
            x="expected_fppg",
            y="actual_fppg",
            color="position",
            size="avg_wopr",
            hover_name="player_name",
            hover_data=["team", "fpoe_per_game", "gms"],
            labels={"expected_fppg": "Expected Half-PPR Points/Game (Opportunity)", 
                    "actual_fppg": "Actual Half-PPR Points/Game"},
            title="Opportunity (xFP) vs Realized Fantasy Points"
        )
        
        # Add a 1:1 parity line
        min_val = min(df_scatter["expected_fppg"].min(), df_scatter["actual_fppg"].min())
        max_val = max(df_scatter["expected_fppg"].max(), df_scatter["actual_fppg"].max())
        fig_scatter.add_shape(
            type="line", line=dict(dash="dash", color="gray", width=1),
            x0=min_val, y0=min_val, x1=max_val, y1=max_val
        )
        
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("No players meet the selected WOPR and Games criteria.")

# -------------------------------------------------------------------
# TAB 3: RAW DATA EXPLORER
# -------------------------------------------------------------------
with tab3:
    st.subheader("Master 50-Metric Data Explorer")
    
    search_term = st.text_input("🔍 Search Player Name", "")
    
    explorer_query = f"""
    SELECT 
        season,
        week,
        player_name,
        position,
        team,
        targets,
        receptions,
        receiving_yards,
        target_share_pct,
        air_yard_share_pct,
        wopr,
        expected_half_ppr_pts,
        actual_half_ppr_pts,
        fpoe
    FROM v_master_fantasy_analytics_50
    WHERE position IN ({','.join([f"'{p}'" for p in position_filter])})
      AND player_name ILIKE '%{search_term}%'
    ORDER BY season DESC, week DESC, wopr DESC
    LIMIT 250;
    """
    
    df_explorer = con.execute(explorer_query).df()
    st.dataframe(df_explorer, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.caption("🤖 Automated Pipeline Execution Engine | Yahoo Diamond Rating Analytics")