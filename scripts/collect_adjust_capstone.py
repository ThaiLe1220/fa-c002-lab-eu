#!/usr/bin/env python3
"""
Adjust Data Collection - Capstone Version

Collects data with ALL new metrics:
- D0 columns (ad_revenue_total_D0, ad_impressions_total_D0)
- paid_impressions, subscrevnt_revenue
- network_cost (was collected but missing in dbt)

Usage:
    python scripts/collect_adjust_capstone.py --days 3
    python scripts/collect_adjust_capstone.py --start 2025-01-08 --end 2025-01-10
"""

import os
import sys
import argparse
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests
import pandas as pd
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

from scripts.utils.snowflake_client import get_snowflake_client

# Load environment
load_dotenv(dotenv_path=".secret/.env")

console = Console()

# Target apps for capstone (same as midtest for consistency)
TARGET_APPS = [
    "video.ai.videogenerator",  # Text to Video FLIX
    "ai.video.generator.text.video",  # AI GPT Generator
    "text.to.video.aivideo.generator",  # Text2Pet
]

# Data directory
CAPSTONE_DIR = project_root / "data" / "capstone"


def fetch_adjust_daily(api_token: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch daily data from Adjust API with ALL new metrics."""
    console.print(f"[cyan]Fetching Adjust API: {start_date} to {end_date}[/cyan]")

    url = "https://automate.adjust.com/reports-service/csv_report"

    params = {
        "dimensions": "app,store_id,day,country_code,country,os_name",
        # ALL metrics including new ones
        "metrics": "installs,clicks,daus,ad_revenue,ad_impressions,network_cost,ad_revenue_total_D0,ad_impressions_total_D0,paid_impressions,subscrevnt_revenue",
        "date_period": f"{start_date}:{end_date}",
        "utc_offset": "+00:00",
    }

    headers = {"Authorization": f"Bearer {api_token}"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=60)
        response.raise_for_status()

        import io
        df = pd.read_csv(io.StringIO(response.text))

        # Filter to target apps only
        df_filtered = df[df["store_id"].isin(TARGET_APPS)].copy()

        console.print(f"[green]✓ Fetched {len(df_filtered):,} rows for target apps[/green]")
        console.print(f"[dim]  Columns: {list(df_filtered.columns)}[/dim]")
        return df_filtered

    except Exception as e:
        console.print(f"[red]✗ API error: {e}[/red]")
        return pd.DataFrame()


def save_to_csv(df: pd.DataFrame, start_date: str, end_date: str):
    """Save data to CSV."""
    if df.empty:
        console.print("[yellow]⚠ No data to save[/yellow]")
        return None

    CAPSTONE_DIR.mkdir(parents=True, exist_ok=True)
    filename = CAPSTONE_DIR / f"adjust_{start_date}_{end_date}.csv"
    df.to_csv(filename, index=False)
    console.print(f"[green]✓ Saved {len(df):,} rows to {filename}[/green]")
    return filename


def load_to_snowflake(df: pd.DataFrame):
    """Load to Snowflake RAW_CAPSTONE.ADJUST_DAILY."""
    if df.empty:
        console.print("[yellow]⚠ No data to load[/yellow]")
        return

    # Add metadata
    batch_timestamp = pd.Timestamp.now()
    batch_id = f"capstone_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    df_load = df.copy()
    df_load["raw_record_id"] = [str(uuid.uuid4()) for _ in range(len(df_load))]
    df_load["batch_id"] = batch_id
    df_load["loaded_at"] = batch_timestamp

    # Convert numeric columns
    numeric_cols = [
        "installs", "clicks", "daus", "ad_revenue", "ad_impressions", "network_cost",
        "ad_revenue_total_D0", "ad_impressions_total_D0", "paid_impressions", "subscrevnt_revenue"
    ]
    for col in numeric_cols:
        if col in df_load.columns:
            df_load[col] = pd.to_numeric(df_load[col], errors='coerce').fillna(0)

    # Uppercase column names for Snowflake
    df_load.columns = df_load.columns.str.upper()

    # Connect and load
    client = get_snowflake_client(schema="RAW_CAPSTONE")

    try:
        conn = client.connect()

        console.print(f"[cyan]Loading {len(df_load):,} rows to RAW_CAPSTONE.ADJUST_DAILY...[/cyan]")

        from snowflake.connector.pandas_tools import write_pandas

        success, nchunks, nrows, _ = write_pandas(
            conn=conn,
            df=df_load,
            table_name="ADJUST_DAILY",
            database="DB_T34",
            schema="RAW_CAPSTONE",
            auto_create_table=False,
            overwrite=False,
            use_logical_type=True,
        )

        if success:
            console.print(f"[green]✓ Loaded {nrows:,} rows to Snowflake[/green]")
        else:
            console.print("[red]✗ Load failed[/red]")

    except Exception as e:
        console.print(f"[red]✗ Snowflake error: {e}[/red]")
        raise

    finally:
        client.close()


def main():
    """Main pipeline execution."""
    parser = argparse.ArgumentParser(description="Adjust Capstone Data Collection")
    parser.add_argument("--days", type=int, default=3, help="Number of days to fetch (default: 3)")
    parser.add_argument("--start", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, help="End date (YYYY-MM-DD)")

    args = parser.parse_args()

    # Calculate date range
    if args.start and args.end:
        start_date = args.start
        end_date = args.end
    else:
        end_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")

    console.print(
        Panel.fit(
            f"[bold cyan]Adjust Capstone Pipeline[/bold cyan]\n"
            f"Period: {start_date} to {end_date}\n"
            f"Apps: {len(TARGET_APPS)} target apps\n"
            f"Schema: RAW_CAPSTONE",
            title="Data Collection",
        )
    )

    # Get API token
    api_token = os.getenv("ADJUST_TOKEN")
    if not api_token:
        console.print("[red]✗ Missing ADJUST_TOKEN in .env[/red]")
        return 1

    try:
        # Fetch data
        df = fetch_adjust_daily(api_token, start_date, end_date)

        if not df.empty:
            # Save to CSV
            save_to_csv(df, start_date, end_date)

            # Load to Snowflake
            load_to_snowflake(df)

            console.print(
                Panel.fit(
                    f"[bold green]✅ Pipeline Complete[/bold green]\n"
                    f"Rows: {len(df):,}\n"
                    f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    title="Success",
                )
            )
        else:
            console.print("[yellow]⚠ No data fetched[/yellow]")

        return 0

    except Exception as e:
        console.print(f"\n[bold red]✗ Pipeline failed: {e}[/bold red]")
        import traceback
        console.print(f"[red]{traceback.format_exc()}[/red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
