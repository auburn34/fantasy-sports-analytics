import sys
import time
from initialize_db import init_database
from load_historical_data import load_history
from sync_2026_rosters import sync_rosters
from generate_50_analytics import create_50_analytics_view
from project_volume import build_projected_volume_views

def run_pipeline():
    start_time = time.time()
    print("=" * 65)
    print("🏈 STARTING MASTER FANTASY ANALYTICS ETL & PRODUCTION PIPELINE")
    print("=" * 65)
    
    try:
        print("\n🚀 [1/5] Initializing DuckDB Schemas...")
        init_database()
        
        print("\n🚀 [2/5] Extracting & Ingesting Historical Player Data...")
        load_history()
        
        print("\n🚀 [3/5] Syncing 2026 Offseason Transactions & Rosters...")
        sync_rosters()
        
        print("\n🚀 [4/5] Compiling Master 50-Metric Analytical View...")
        create_50_analytics_view()

        print("\n🚀 [5/5] Building 2026 Context-Adjusted Projected Volume Engine...")
        build_projected_volume_views()
        
        elapsed_time = round(time.time() - start_time, 2)
        print("\n" + "=" * 65)
        print(f"🎉 PIPELINE EXECUTION COMPLETE! Total Execution Time: {elapsed_time}s")
        print("=" * 65)
        
    except Exception as e:
        print(f"\n❌ PIPELINE FAILED: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()