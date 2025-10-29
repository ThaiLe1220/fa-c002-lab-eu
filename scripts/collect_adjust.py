#!/usr/bin/env python3
"""
Adjust Daily Data Collection - Pure RAW Pipeline

Two modes:
1. --historical: Fetch last 7 days (excluding yesterday), append to local CSV
2. --realtime: Fetch yesterday only, load to Snowflake

NO TRANSFORMATIONS - stores exact API response.

Usage:
    python scripts/collect_adjust.py --historical
    python scripts/collect_adjust.py --realtime
"""

import os
import sys
import argparse
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

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

# Historical data directory
HISTORICAL_DIR = project_root / "data" / "historical"
HISTORICAL_FILE = HISTORICAL_DIR / "adjust_historical.csv"


def fetch_adjust_daily(api_token: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch daily data from Adjust API (NO hour dimension).

    Args:
        api_token: Adjust API token
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        DataFrame with daily grain (no hour column)
    """

    console.print(f"[cyan]Fetching Adjust API: {start_date} to {end_date}[/cyan]")

    url = "https://automate.adjust.com/reports-service/csv_report"

    params = {
        "dimensions": "app,store_id,day,country_code,country,os_name",  # NO HOUR - daily grain with ISO codes
        "metrics": "installs,clicks,daus,ad_revenue,ad_impressions,network_cost",
        "date_period": f"{start_date}:{end_date}",
        "utc_offset": "+00:00",
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


def get_latest_date_from_csv() -> Optional[datetime.date]:
    """Get latest date from historical CSV file."""

    if not HISTORICAL_FILE.exists():
        return None

    try:
        df = pd.read_csv(HISTORICAL_FILE)
        if df.empty or "day" not in df.columns:
            return None

        latest = pd.to_datetime(df["day"]).max().date()
        return latest

    except Exception as e:
        console.print(f"[yellow]⚠ Could not read historical file: {e}[/yellow]")
        return None


def append_to_csv(df: pd.DataFrame):
    """Append data to historical CSV file."""

    if df.empty:
        console.print("[yellow]⚠ No data to append[/yellow]")
        return

    # Create directory if not exists
    HISTORICAL_DIR.mkdir(parents=True, exist_ok=True)

    # Check if file exists
    file_exists = HISTORICAL_FILE.exists()

    # Append to CSV
    df.to_csv(HISTORICAL_FILE, mode="a", header=not file_exists, index=False)

    console.print(f"[green]✓ Appended {len(df):,} rows to {HISTORICAL_FILE}[/green]")

    # Show summary
    try:
        full_df = pd.read_csv(HISTORICAL_FILE)
        console.print(f"[cyan]Total historical rows: {len(full_df):,}[/cyan]")

        if "day" in full_df.columns:
            date_range = f"{full_df['day'].min()} to {full_df['day'].max()}"
            console.print(f"[cyan]Date range: {date_range}[/cyan]")
    except:
        pass


def load_to_snowflake(df: pd.DataFrame):
    """
    Load DataFrame to Snowflake RAW.ADJUST_DAILY.

    Args:
        df: DataFrame with API columns
    """

    if df.empty:
        console.print("[yellow]⚠ No data to load[/yellow]")
        return

    # Add loaded_at timestamp (pandas-native for Snowflake compatibility)
    df["loaded_at"] = pd.Timestamp.now()

    # Convert column names to UPPERCASE (Snowflake convention)
    df.columns = df.columns.str.upper()

    client = get_snowflake_client()

    try:
        conn = client.connect()

        console.print(f"[cyan]Loading {len(df):,} rows to RAW.ADJUST_DAILY...[/cyan]")

        # Write directly to Snowflake using pandas
        from snowflake.connector.pandas_tools import write_pandas

        success, nchunks, nrows, _ = write_pandas(
            conn=conn,
            df=df,
            table_name="ADJUST_DAILY",
            database="DB_T34",
            schema="RAW",
            auto_create_table=False,
            overwrite=False,
            use_logical_type=True,  # Fix datetime handling
        )

        if success:
            console.print(f"[green]✓ Loaded {nrows:,} rows to RAW.ADJUST_DAILY[/green]")
        else:
            console.print(f"[red]✗ Load failed[/red]")

    except Exception as e:
        console.print(f"[red]✗ Snowflake error: {e}[/red]")
        raise

    finally:
        client.close()


def run_historical(api_token: str):
    """
    Historical mode: Fetch last 7 days (excluding yesterday), append to CSV.

    Logic:
    - If no CSV: Fetch [today-8] to [today-2] (7 days)
    - If CSV exists: Fetch from [latest_date+1] to [today-2]
    """

    console.print("\n[bold]Mode: Historical (Batch)[/bold]")

    # Get latest date from CSV
    latest_date = get_latest_date_from_csv()

    # Calculate date range
    day_before_yesterday = (datetime.now() - timedelta(days=2)).date()

    if latest_date is None:
        # No historical data - fetch last 7 days
        start_date = day_before_yesterday - timedelta(days=6)
        console.print(
            f"[cyan]No historical data found. Fetching initial 7 days.[/cyan]"
        )
    else:
        # Update from last date to day before yesterday
        start_date = latest_date + timedelta(days=1)
        console.print(f"[cyan]Historical data found (latest: {latest_date})[/cyan]")
        console.print(
            f"[cyan]Updating from {start_date} to {day_before_yesterday}[/cyan]"
        )

    # Validate date range
    if start_date > day_before_yesterday:
        console.print(
            f"[yellow]⚠ Historical data is up to date (latest: {latest_date})[/yellow]"
        )
        console.print(f"[yellow]No new data to fetch[/yellow]")
        return 0

    start_str = start_date.strftime("%Y-%m-%d")
    end_str = day_before_yesterday.strftime("%Y-%m-%d")

    # Fetch data
    console.print(f"\n[bold]Fetching: {start_str} to {end_str}[/bold]")
    df = fetch_adjust_daily(api_token, start_str, end_str)

    if df.empty:
        console.print("[yellow]⚠ No data fetched[/yellow]")
        return 0

    # Append to CSV
    append_to_csv(df)

    return 0


def load_realtime_rows(rows_df: pd.DataFrame, label: str, delay: float = 0.1):
    """Load rows one-by-one with delay for demo effect."""
    for idx, row in rows_df.iterrows():
        single_row_df = pd.DataFrame([row])
        load_to_snowflake(single_row_df)
        console.print(f"  [green]✓[/green] {label} row {idx + 1} inserted")
        if idx < rows_df.index[-1]:
            time.sleep(delay)


def run_realtime(api_token: str):
    """
    Realtime mode: Fetch yesterday only, load to Snowflake.

    Strategy:
    - Realtime demo: First 5 + Last 5 rows (row-by-row with delay)
    - Bulk load: Middle rows (fast batch insert)
    - Multithreaded: Bulk and realtime load in parallel (6 workers)

    Note: API data needs 1 day to update. Running at 11:30am ensures
    yesterday's complete data is available.
    """

    console.print("\n[bold]Mode: Realtime (Daily Update)[/bold]")

    # Yesterday's date
    yesterday = (datetime.now() - timedelta(days=1)).date()
    yesterday_str = yesterday.strftime("%Y-%m-%d")

    console.print(f"[cyan]Fetching yesterday's data: {yesterday_str}[/cyan]")
    console.print(
        f"[dim]Note: Running at 11:30am ensures complete data (1-day delay)[/dim]"
    )

    # Fetch data
    df = fetch_adjust_daily(api_token, yesterday_str, yesterday_str)

    if df.empty:
        console.print("[yellow]⚠ No data fetched[/yellow]")
        return 0

    # Split into first 5, middle bulk, last 5
    DEMO_ROWS = 5
    total_rows = len(df)

    if total_rows <= DEMO_ROWS * 2:
        # If total rows <= 10, do all row-by-row
        first_df = df.iloc[: total_rows // 2].copy()
        bulk_df = pd.DataFrame()
        last_df = df.iloc[total_rows // 2 :].copy()
    else:
        # Split: first 5 + middle bulk + last 5
        first_df = df.iloc[:DEMO_ROWS].copy()
        bulk_df = df.iloc[DEMO_ROWS:-DEMO_ROWS].copy()
        last_df = df.iloc[-DEMO_ROWS:].copy()

    console.print(f"\n[bold]Loading Strategy:[/bold]")
    console.print(f"  First {len(first_df)} rows: Realtime (row-by-row)")
    console.print(f"  Middle {len(bulk_df):,} rows: Bulk (fast)")
    console.print(f"  Last {len(last_df)} rows: Realtime (row-by-row)")
    console.print(
        f"[dim]Using multithreading (6 workers) with 0.1s delay per realtime row...[/dim]\n"
    )

    # Use ThreadPoolExecutor for parallel loading
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = []

        # Submit realtime first 5 rows
        if not first_df.empty:
            futures.append(executor.submit(load_realtime_rows, first_df, "First", 0.1))

        # Submit bulk load
        if not bulk_df.empty:
            futures.append(executor.submit(load_to_snowflake, bulk_df))

        # Submit realtime last 5 rows
        if not last_df.empty:
            futures.append(executor.submit(load_realtime_rows, last_df, "Last", 0.1))

        # Wait for all tasks to complete
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                console.print(f"[red]✗ Error: {e}[/red]")

    console.print(
        f"\n[green]✓ Total loaded: {total_rows:,} rows ({len(first_df)} first + {len(bulk_df):,} bulk + {len(last_df)} last)[/green]"
    )

    return 0


def main():
    """Main pipeline execution."""

    parser = argparse.ArgumentParser(
        description="Adjust Daily Data Collection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch last 7 days (excluding yesterday), append to CSV
  python scripts/collect_adjust.py --historical

  # Fetch yesterday only, load to Snowflake
  python scripts/collect_adjust.py --realtime
        """,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--historical",
        action="store_true",
        help="Batch mode: Fetch last 7 days (excluding yesterday), append to CSV",
    )
    group.add_argument(
        "--realtime",
        action="store_true",
        help="Realtime mode: Fetch yesterday only, load to Snowflake",
    )

    args = parser.parse_args()

    # Header
    mode = "Historical (Batch)" if args.historical else "Realtime (Daily)"
    console.print(
        Panel.fit(
            f"[bold cyan]Adjust Daily Pipeline[/bold cyan]\n"
            f"Mode: {mode}\n"
            f"Grain: Daily (no hour dimension)\n"
            f"Strategy: Pure RAW (no transformations)",
            title="Data Collection",
        )
    )

    # Get API token
    api_token = os.getenv("ADJUST_TOKEN")

    if not api_token:
        console.print("[red]✗ Missing ADJUST_TOKEN in .env[/red]")
        return 1

    try:
        # Run appropriate mode
        if args.historical:
            result = run_historical(api_token)
        else:  # realtime
            result = run_realtime(api_token)

        # Success summary
        if result == 0:
            console.print(
                Panel.fit(
                    f"[bold green]✓ Pipeline Complete[/bold green]\n"
                    f"Mode: {mode}\n"
                    f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    title="Success",
                )
            )

        return result

    except Exception as e:
        console.print(f"\n[bold red]✗ Pipeline failed: {e}[/bold red]")
        import traceback

        console.print(f"[red]{traceback.format_exc()}[/red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
