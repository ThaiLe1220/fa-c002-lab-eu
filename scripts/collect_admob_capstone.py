#!/usr/bin/env python3
"""
AdMob Data Collection - Capstone Version

Collects AdMob data to RAW_CAPSTONE.ADMOB_DAILY

Usage:
    python scripts/collect_admob_capstone.py --days 3
    python scripts/collect_admob_capstone.py --start 2025-01-08 --end 2025-01-10
"""

import os
import sys
import pickle
import argparse
import uuid
from datetime import datetime, timedelta
from pathlib import Path

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

# Full portfolio - no filter, collect all apps
# Previously filtered to 3 apps for midtest, now collecting everything

# Data directory
CAPSTONE_DIR = project_root / "data" / "capstone"


def authenticate_admob(publisher_id: str):
    """Authenticate with AdMob using saved credentials."""
    secret_dir = Path(".secret")
    token_file = secret_dir / f"token_{publisher_id}.pickle"

    if not token_file.exists():
        raise FileNotFoundError(f"Token file not found: {token_file}")

    try:
        with open(token_file, "rb") as token:
            credentials = pickle.load(token)

        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())

        service = build("admob", "v1", credentials=credentials)
        console.print(f"[green]✓ Authenticated: {publisher_id}[/green]")
        return service

    except Exception as e:
        raise RuntimeError(f"AdMob authentication failed: {str(e)}")


def get_approved_apps(service, publisher_id: str) -> dict:
    """Get ALL approved apps with package IDs from AdMob."""
    console.print("[cyan]Fetching app metadata...[/cyan]")

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
            if app.get("appApprovalState") != "APPROVED":
                continue

            if "linkedAppInfo" not in app:
                continue

            linked_info = app["linkedAppInfo"]
            if "displayName" in linked_info and "appStoreId" in linked_info:
                # Full portfolio - no filter
                valid_apps[app["appId"]] = {
                    "displayName": linked_info["displayName"],
                    "appStoreId": linked_info["appStoreId"],
                }

        next_page_token = response.get("nextPageToken", None)

    console.print(f"[green]✓ Found {len(valid_apps)} approved apps[/green]")
    return valid_apps


def fetch_admob_raw(
    service, publisher_id: str, start_date: str, end_date: str
) -> pd.DataFrame:
    """Fetch raw AdMob data for ALL approved apps."""
    console.print(f"[cyan]Fetching AdMob API: {start_date} to {end_date}[/cyan]")

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
            "dimensions": ["APP", "DATE", "COUNTRY", "PLATFORM"],
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

        rows = []

        if isinstance(response, list):
            for item in response[1:]:
                if "row" in item:
                    row = item["row"]
                    dim = row.get("dimensionValues", {})
                    met = row.get("metricValues", {})

                    internal_app_id = dim.get("APP", {}).get("value")
                    app_info = approved_apps.get(internal_app_id, {})

                    # Full portfolio - include all approved apps
                    if app_info:
                        rows.append(
                            {
                                "date": dim.get("DATE", {}).get("value"),
                                "app_name": app_info.get("displayName", ""),
                                "app_store_id": app_info.get("appStoreId", ""),
                                "country_code": dim.get("COUNTRY", {}).get("value"),
                                "platform": dim.get("PLATFORM", {}).get("value"),
                                "estimated_earnings": met.get(
                                    "ESTIMATED_EARNINGS", {}
                                ).get("microsValue"),
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
        console.print(f"[green]✓ Fetched {len(df):,} rows (all apps)[/green]")
        return df

    except Exception as e:
        console.print(f"[red]✗ API error: {e}[/red]")
        return pd.DataFrame()


def save_to_csv(df: pd.DataFrame, start_date: str, end_date: str):
    """Save data to CSV."""
    if df.empty:
        console.print("[yellow]⚠ No data to save[/yellow]")
        return None

    CAPSTONE_DIR.mkdir(parents=True, exist_ok=True)
    filename = CAPSTONE_DIR / f"admob_{start_date}_{end_date}.csv"
    df.to_csv(filename, index=False)
    console.print(f"[green]✓ Saved {len(df):,} rows to {filename}[/green]")
    return filename


def load_to_snowflake(df: pd.DataFrame):
    """Load to Snowflake RAW_CAPSTONE.ADMOB_DAILY."""
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
        "estimated_earnings", "ad_impressions", "ad_clicks",
        "ad_requests", "matched_requests", "observed_ecpm"
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

        console.print(f"[cyan]Loading {len(df_load):,} rows to RAW_CAPSTONE.ADMOB_DAILY...[/cyan]")

        from snowflake.connector.pandas_tools import write_pandas

        success, nchunks, nrows, _ = write_pandas(
            conn=conn,
            df=df_load,
            table_name="ADMOB_DAILY",
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
    parser = argparse.ArgumentParser(description="AdMob Capstone Data Collection")
    parser.add_argument("--days", type=int, default=3, help="Number of days to fetch (default: 3)")
    parser.add_argument("--start", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, help="End date (YYYY-MM-DD)")
    parser.add_argument(
        "--publishers",
        type=str,
        nargs="+",
        default=[
            "pub-4738062221647171",
            "pub-3717786786472633",
            "pub-4109716399396805",
        ],
        help="Publisher IDs",
    )

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
            f"[bold cyan]AdMob Capstone Pipeline[/bold cyan]\n"
            f"Period: {start_date} to {end_date}\n"
            f"Publishers: {len(args.publishers)}\n"
            f"Apps: Full portfolio (all approved)\n"
            f"Schema: RAW_CAPSTONE",
            title="Data Collection",
        )
    )

    all_data = []

    for i, publisher_id in enumerate(args.publishers, 1):
        console.print(
            f"\n[bold cyan]═══ Publisher {i}/{len(args.publishers)}: {publisher_id} ═══[/bold cyan]"
        )

        try:
            # Authenticate
            service = authenticate_admob(publisher_id)

            # Fetch data
            df = fetch_admob_raw(service, publisher_id, start_date, end_date)

            if not df.empty:
                all_data.append(df)

        except Exception as e:
            console.print(f"[red]✗ Publisher {publisher_id} error: {e}[/red]")
            continue

    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        console.print(f"\n[cyan]Total rows: {len(combined_df):,}[/cyan]")

        # Save to CSV
        save_to_csv(combined_df, start_date, end_date)

        # Load to Snowflake
        load_to_snowflake(combined_df)

        console.print(
            Panel.fit(
                f"[bold green]✅ Pipeline Complete[/bold green]\n"
                f"Rows: {len(combined_df):,}\n"
                f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                title="Success",
            )
        )
    else:
        console.print("[yellow]⚠ No data collected[/yellow]")

    return 0


if __name__ == "__main__":
    sys.exit(main())
