#!/usr/bin/env python3
"""
Adjust Hourly Data Collection - Pure RAW Pipeline

Fetches hourly data from Adjust API and loads to Snowflake RAW table.
NO TRANSFORMATIONS - stores exact API response.

Usage:
    python scripts/collect_adjust.py --hours 1
    python scripts/collect_adjust.py --hours 24  # Backfill last day
"""

import os
import sys
import argparse
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


def fetch_adjust_raw(api_token: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch raw data from Adjust API (CSV format).

    Args:
        api_token: Adjust API token
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        DataFrame with exact API columns
    """

    console.print(f"[cyan]Fetching Adjust API: {start_date} to {end_date}[/cyan]")

    url = "https://automate.adjust.com/reports-service/csv_report"

    params = {
        "dimensions": "app,store_id,day,hour,country,os_name",
        "metrics": "installs,clicks,daus,ad_revenue,ad_impressions,ad_revenue_total_d0,ad_impressions_total_d0,network_cost,network_cost_diff",
        "date_period": f"{start_date}:{end_date}",
        "utc_offset": "+00:00"
    }

    headers = {"Authorization": f"Bearer {api_token}"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=60)
        response.raise_for_status()

        # Parse CSV to DataFrame
        import io
        df = pd.read_csv(io.StringIO(response.text))

        console.print(f"[green]✓ Fetched {len(df):,} rows[/green]")

        return df

    except Exception as e:
        console.print(f"[red]✗ API error: {e}[/red]")
        return pd.DataFrame()


def load_to_snowflake(df: pd.DataFrame):
    """
    Load raw DataFrame to Snowflake (exact copy, no transformations).

    Args:
        df: DataFrame with API columns
    """

    if df.empty:
        console.print("[yellow]⚠ No data to load[/yellow]")
        return

    # Add loaded_at timestamp
    df["loaded_at"] = datetime.now()

    # Convert column names to UPPERCASE (Snowflake convention)
    df.columns = df.columns.str.upper()

    client = get_snowflake_client()

    try:
        conn = client.connect()

        console.print(f"[cyan]Loading {len(df):,} rows to RAW.ADJUST_HOURLY...[/cyan]")

        # Write directly to Snowflake using pandas
        from snowflake.connector.pandas_tools import write_pandas

        success, nchunks, nrows, _ = write_pandas(
            conn=conn,
            df=df,
            table_name="ADJUST_HOURLY",
            database="DB_T34",
            schema="RAW",
            auto_create_table=False,
            overwrite=False
        )

        if success:
            console.print(f"[green]✓ Loaded {nrows:,} rows to RAW.ADJUST_HOURLY[/green]")
        else:
            console.print(f"[red]✗ Load failed[/red]")

    except Exception as e:
        console.print(f"[red]✗ Snowflake error: {e}[/red]")
        raise

    finally:
        client.close()


def main():
    """Main pipeline execution."""

    parser = argparse.ArgumentParser(description="Adjust Hourly RAW Data Collection")
    parser.add_argument("--hours", type=int, default=1, help="Number of hours to fetch (default: 1)")
    args = parser.parse_args()

    console.print(Panel.fit(
        "[bold cyan]Adjust RAW Pipeline[/bold cyan]\n"
        f"Fetching last {args.hours} hour(s)\n"
        "Mode: Pure RAW (no transformations)",
        title="Data Collection"
    ))

    # Get API token
    api_token = os.getenv("ADJUST_TOKEN")

    if not api_token:
        console.print("[red]✗ Missing ADJUST_TOKEN in .env[/red]")
        return 1

    # Calculate date range
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=(args.hours // 24) if args.hours >= 24 else 1)

    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    try:
        # Fetch raw data
        console.print("\n[bold]Step 1: Fetch from Adjust API[/bold]")
        raw_df = fetch_adjust_raw(api_token, start_str, end_str)

        if raw_df.empty:
            console.print("[yellow]⚠ No data fetched[/yellow]")
            return 0

        # Load to Snowflake (no transformations)
        console.print("\n[bold]Step 2: Load to Snowflake RAW[/bold]")
        load_to_snowflake(raw_df)

        # Success
        console.print(Panel.fit(
            f"[bold green]✓ Pipeline Complete[/bold green]\n"
            f"Date Range: {start_str} to {end_str}\n"
            f"Rows Loaded: {len(raw_df):,}\n"
            f"Loaded At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            title="Success"
        ))

        return 0

    except Exception as e:
        console.print(f"\n[bold red]✗ Pipeline failed: {e}[/bold red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
