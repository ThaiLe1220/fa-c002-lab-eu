#!/usr/bin/env python3
"""
AdMob Daily Data Collection - Pure RAW Pipeline

Two modes:
1. --historical: Fetch last 7 days (excluding yesterday), append to local CSV
2. --realtime: Fetch yesterday only, load to Snowflake

NO TRANSFORMATIONS - stores exact API response (flattened).

Usage:
    python scripts/collect_admob.py --historical
    python scripts/collect_admob.py --realtime
"""

import os
import sys
import pickle
import argparse
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
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
HISTORICAL_FILE = HISTORICAL_DIR / "admob_historical.csv"


def authenticate_admob(publisher_id: str):
    """
    Authenticate with AdMob using saved credentials.

    Args:
        publisher_id: AdMob publisher ID (pub-xxxxx)

    Returns:
        AdMob API service object
    """

    secret_dir = Path(".secret")
    token_file = secret_dir / f"token_{publisher_id}.pickle"

    if not token_file.exists():
        raise FileNotFoundError(f"Token file not found: {token_file}")

    try:
        with open(token_file, "rb") as token:
            credentials = pickle.load(token)

        # Refresh if expired
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())

        service = build("admob", "v1", credentials=credentials)
        console.print(f"[green]✓ Authenticated: {publisher_id}[/green]")
        return service

    except Exception as e:
        raise RuntimeError(f"AdMob authentication failed: {str(e)}")


def get_approved_apps(service, publisher_id: str) -> dict:
    """
    Get approved apps with package IDs from AdMob.

    Args:
        service: AdMob API service
        publisher_id: Publisher ID

    Returns:
        Dict mapping internal app_id to {displayName, appStoreId}
    """

    console.print(f"[cyan]Fetching app metadata (for package IDs)...[/cyan]")

    valid_apps = {}
    next_page_token = ""

    while next_page_token is not None:
        response = (
            service.accounts()
            .apps()
            .list(
                pageSize=1000,
                pageToken=next_page_token,
                parent=f"accounts/{publisher_id}",
            )
            .execute()
        )

        if not response:
            break

        for app in response.get("apps", []):
            # Only approved apps
            if app.get("appApprovalState") != "APPROVED":
                continue

            # Must have linkedAppInfo with package ID
            if "linkedAppInfo" not in app:
                continue

            linked_info = app["linkedAppInfo"]
            if "displayName" in linked_info and "appStoreId" in linked_info:
                valid_apps[app["appId"]] = {
                    "displayName": linked_info["displayName"],
                    "appStoreId": linked_info["appStoreId"],
                }

        next_page_token = response.get("nextPageToken", None)

    console.print(
        f"[green]✓ Found {len(valid_apps)} approved apps with package IDs[/green]"
    )
    return valid_apps


def fetch_admob_raw(
    service, publisher_id: str, start_date: str, end_date: str
) -> pd.DataFrame:
    """
    Fetch raw AdMob data (exact API response, flattened).

    Args:
        service: AdMob API service
        publisher_id: Publisher ID
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        DataFrame with exact API fields (no transformations)
    """

    console.print(f"[cyan]Fetching AdMob API: {start_date} to {end_date}[/cyan]")

    # Get app metadata with package IDs
    approved_apps = get_approved_apps(service, publisher_id)

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    request_body = {
        "report_spec": {
            "date_range": {
                "start_date": {
                    "year": start_dt.year,
                    "month": start_dt.month,
                    "day": start_dt.day,
                },
                "end_date": {
                    "year": end_dt.year,
                    "month": end_dt.month,
                    "day": end_dt.day,
                },
            },
            "dimensions": ["APP", "DATE", "COUNTRY", "PLATFORM"],  # Match Adjust grain
            "metrics": [
                "ESTIMATED_EARNINGS",
                "IMPRESSIONS",
                "CLICKS",
                "AD_REQUESTS",
                "MATCHED_REQUESTS",
                "OBSERVED_ECPM",
            ],
            "localization_settings": {"currency_code": "USD"},
        }
    }

    try:
        response = (
            service.accounts()
            .mediationReport()
            .generate(parent=f"accounts/{publisher_id}", body=request_body)
            .execute()
        )

        # Parse response - extract raw values (no transformations)
        rows = []

        if isinstance(response, list):
            # Skip first item (header)
            for item in response[1:]:
                if "row" in item:
                    row = item["row"]
                    dim = row.get("dimensionValues", {})
                    met = row.get("metricValues", {})

                    # Get internal app ID and map to package ID
                    internal_app_id = dim.get("APP", {}).get("value")
                    app_info = approved_apps.get(internal_app_id, {})

                    # Extract raw values (with platform for matching Adjust grain)
                    rows.append(
                        {
                            "date": dim.get("DATE", {}).get("value"),
                            "app_name": app_info.get("displayName", ""),
                            "app_store_id": app_info.get("appStoreId", ""),
                            "country_code": dim.get("COUNTRY", {}).get("value"),
                            "platform": dim.get("PLATFORM", {}).get("value"),
                            "estimated_earnings": met.get("ESTIMATED_EARNINGS", {}).get(
                                "microsValue"
                            ),
                            "ad_impressions": met.get("IMPRESSIONS", {}).get(
                                "integerValue"
                            ),
                            "ad_clicks": met.get("CLICKS", {}).get("integerValue"),
                            "ad_requests": met.get("AD_REQUESTS", {}).get(
                                "integerValue"
                            ),
                            "matched_requests": met.get("MATCHED_REQUESTS", {}).get(
                                "integerValue"
                            ),
                            "observed_ecpm": met.get("OBSERVED_ECPM", {}).get(
                                "microsValue"
                            ),
                        }
                    )

        df = pd.DataFrame(rows)

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
        if df.empty or "date" not in df.columns:
            return None

        # AdMob date format is YYYYMMDD string
        latest_str = df["date"].astype(str).max()
        latest = datetime.strptime(latest_str, "%Y%m%d").date()
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

        if "date" in full_df.columns:
            date_range = f"{full_df['date'].min()} to {full_df['date'].max()}"
            console.print(f"[cyan]Date range: {date_range}[/cyan]")
    except:
        pass


def load_to_snowflake(df: pd.DataFrame):
    """
    Load DataFrame to Snowflake RAW.ADMOB_DAILY.

    Args:
        df: DataFrame with API columns
    """

    if df.empty:
        console.print("[yellow]⚠ No data to load[/yellow]")
        return

    # Add metadata (pandas-native timestamp for Snowflake compatibility)
    df["loaded_at"] = pd.Timestamp.now()

    # Convert column names to UPPERCASE (Snowflake convention)
    df.columns = df.columns.str.upper()

    client = get_snowflake_client()

    try:
        conn = client.connect()

        console.print(f"[cyan]Loading {len(df):,} rows to RAW.ADMOB_DAILY...[/cyan]")

        # Write directly to Snowflake using pandas
        from snowflake.connector.pandas_tools import write_pandas

        success, nchunks, nrows, _ = write_pandas(
            conn=conn,
            df=df,
            table_name="ADMOB_DAILY",
            database="DB_T34",
            schema="RAW",
            auto_create_table=False,
            overwrite=False,
            use_logical_type=True,  # Fix datetime handling
        )

        if success:
            console.print(f"[green]✓ Loaded {nrows:,} rows to RAW.ADMOB_DAILY[/green]")
        else:
            console.print(f"[red]✗ Load failed[/red]")

    except Exception as e:
        console.print(f"[red]✗ Snowflake error: {e}[/red]")
        raise

    finally:
        client.close()


def run_historical(service, publisher_id: str, start_str: str, end_str: str):
    """
    Historical mode: Fetch data for date range.

    Note: Date range determined by main() to avoid multi-publisher CSV conflicts.
    """

    console.print(f"\n[bold]Fetching: {start_str} to {end_str}[/bold]")
    df = fetch_admob_raw(service, publisher_id, start_str, end_str)

    if df.empty:
        console.print("[yellow]⚠ No data fetched[/yellow]")
        return None

    return df


def load_realtime_rows(rows_df: pd.DataFrame, label: str, delay: float = 0.1):
    """Load rows one-by-one with delay for demo effect."""
    for idx, row in rows_df.iterrows():
        single_row_df = pd.DataFrame([row])
        load_to_snowflake(single_row_df)
        console.print(f"  [green]✓[/green] {label} row {idx + 1} inserted")
        if idx < rows_df.index[-1]:
            time.sleep(delay)


def run_realtime(service, publisher_id: str):
    """
    Realtime mode: Fetch yesterday only, load to Snowflake.

    Strategy:
    - Realtime demo: First 5 + Last 5 rows (row-by-row with delay)
    - Bulk load: Middle rows (fast batch insert)
    - Multithreaded: Bulk and realtime load in parallel (6 workers)

    Note: AdMob data needs 1 day to finalize. Running at 11:30am ensures
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
    df = fetch_admob_raw(service, publisher_id, yesterday_str, yesterday_str)

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
        description="AdMob Daily Data Collection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch last 7 days (excluding yesterday), append to CSV
  python scripts/collect_admob.py --historical

  # Fetch yesterday only, load to Snowflake
  python scripts/collect_admob.py --realtime
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

    parser.add_argument(
        "--publishers",
        type=str,
        nargs="+",
        default=[
            "pub-4738062221647171",
            "pub-3717786786472633",
            "pub-4109716399396805",
        ],
        help="Publisher IDs (default: all 3 publishers)",
    )

    args = parser.parse_args()

    # Header
    mode = "Historical (Batch)" if args.historical else "Realtime (Daily)"
    console.print(
        Panel.fit(
            f"[bold cyan]AdMob Daily Pipeline[/bold cyan]\n"
            f"Mode: {mode}\n"
            f"Grain: Daily\n"
            f"Publishers: {len(args.publishers)}\n"
            f"Strategy: Pure RAW (no transformations)",
            title="Data Collection",
        )
    )

    total_success = 0
    total_failed = 0
    all_data = []

    # For historical mode: Calculate date range ONCE for all publishers
    if args.historical:
        console.print("\n[bold]Mode: Historical (Batch)[/bold]")

        # Get latest date from CSV
        latest_date = get_latest_date_from_csv()
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
        console.print(
            f"[cyan]Date range for ALL publishers: {start_str} to {end_str}[/cyan]"
        )

    # Loop through all publishers
    for i, publisher_id in enumerate(args.publishers, 1):
        console.print(
            f"\n[bold cyan]═══ Publisher {i}/{len(args.publishers)}: {publisher_id} ═══[/bold cyan]"
        )

        try:
            # Authenticate
            console.print("\n[bold]Step 1: Authenticate[/bold]")
            service = authenticate_admob(publisher_id)

            # Run appropriate mode
            console.print("\n[bold]Step 2: Fetch Data[/bold]")
            if args.historical:
                # Pass same date range to all publishers
                df = run_historical(service, publisher_id, start_str, end_str)
                if df is not None:
                    all_data.append(df)
                    total_success += 1
                    console.print(
                        f"[green]✓ Publisher {publisher_id}: {len(df):,} rows[/green]"
                    )
                else:
                    console.print(
                        f"[yellow]⚠ Publisher {publisher_id}: No data[/yellow]"
                    )
            else:  # realtime
                result = run_realtime(service, publisher_id)
                if result == 0:
                    total_success += 1
                    console.print(f"[green]✓ Publisher {publisher_id} complete[/green]")
                else:
                    total_failed += 1
                    console.print(f"[red]✗ Publisher {publisher_id} failed[/red]")

        except Exception as e:
            total_failed += 1
            console.print(f"[red]✗ Publisher {publisher_id} error: {e}[/red]")
            continue

    # For historical mode: Combine all publishers' data and append ONCE
    if args.historical and all_data:
        console.print(
            f"\n[bold]Combining data from {len(all_data)} publisher(s)...[/bold]"
        )
        combined_df = pd.concat(all_data, ignore_index=True)
        console.print(f"[cyan]Total rows: {len(combined_df):,}[/cyan]")
        append_to_csv(combined_df)

    # Final summary
    console.print(
        Panel.fit(
            f"[bold cyan]Pipeline Complete[/bold cyan]\n"
            f"Mode: {mode}\n"
            f"Publishers: {len(args.publishers)}\n"
            f"[green]✓ Success: {total_success}[/green]\n"
            f"[red]✗ Failed: {total_failed}[/red]\n"
            f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            title="Summary",
        )
    )

    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
