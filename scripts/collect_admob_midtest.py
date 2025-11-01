#!/usr/bin/env python3
"""
AdMob Data Collection - Mid-Course Test Version

Simplified for demo:
- Only 3 apps
- Last 7 days automatically
- Batch mode: Same loaded_at timestamp
- Realtime mode: Staggered loaded_at timestamps
- Adds UUID for data lineage tracking
- Alters data ±50% randomly before Snowflake load

Usage:
    python scripts/collect_admob_midtest.py --batch
    python scripts/collect_admob_midtest.py --realtime
"""

import os
import sys
import pickle
import argparse
import time
import uuid
import random
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

# Target apps for mid-course test
TARGET_APPS = [
    "video.ai.videogenerator",  # Text to Video FLIX
    "ai.video.generator.text.video",  # AI GPT Generator
    "text.to.video.aivideo.generator",  # Text2Pet
]

# Data directory
MIDTEST_DIR = project_root / "data" / "midtest"
MIDTEST_FILE = MIDTEST_DIR / "admob_midtest.csv"


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
    """Get approved apps with package IDs from AdMob."""
    console.print(f"[cyan]Fetching app metadata...[/cyan]")

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
                app_store_id = linked_info["appStoreId"]
                # Filter to target apps only
                if app_store_id in TARGET_APPS:
                    valid_apps[app["appId"]] = {
                        "displayName": linked_info["displayName"],
                        "appStoreId": app_store_id,
                    }

        next_page_token = response.get("nextPageToken", None)

    console.print(f"[green]✓ Found {len(valid_apps)} target apps[/green]")
    return valid_apps


def fetch_admob_raw(
    service, publisher_id: str, start_date: str, end_date: str
) -> pd.DataFrame:
    """Fetch raw AdMob data for target apps only."""
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

                    # Only include target apps
                    if app_info.get("appStoreId") in TARGET_APPS:
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
        console.print(f"[green]✓ Fetched {len(df):,} rows for target apps[/green]")
        return df

    except Exception as e:
        console.print(f"[red]✗ API error: {e}[/red]")
        return pd.DataFrame()


def alter_data(df: pd.DataFrame) -> pd.DataFrame:
    """Alter numeric data by ±50% randomly (except date/app/country)."""
    df_altered = df.copy()

    numeric_cols = [
        "estimated_earnings",
        "ad_impressions",
        "ad_clicks",
        "ad_requests",
        "matched_requests",
        "observed_ecpm",
    ]

    for col in numeric_cols:
        if col in df_altered.columns:
            # Convert to numeric first (handles string values from API)
            df_altered[col] = pd.to_numeric(df_altered[col], errors="coerce")
            # Apply random multiplier between 0.5 and 1.5 (±50%)
            df_altered[col] = df_altered[col].apply(
                lambda x: (
                    int(x * random.uniform(0.5, 1.5)) if pd.notna(x) and x != 0 else x
                )
            )

    return df_altered


def save_to_csv(df: pd.DataFrame):
    """Save original data to CSV."""
    if df.empty:
        console.print("[yellow]⚠ No data to save[/yellow]")
        return

    MIDTEST_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(MIDTEST_FILE, index=False)
    console.print(f"[green]✓ Saved {len(df):,} rows to {MIDTEST_FILE}[/green]")


def load_to_snowflake_batch(df: pd.DataFrame):
    """Load to Snowflake in batch mode (same loaded_at)."""
    if df.empty:
        console.print("[yellow]⚠ No data to load[/yellow]")
        return

    # Alter data
    df_altered = alter_data(df)

    # Add metadata
    batch_timestamp = pd.Timestamp.now()
    batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    df_altered["raw_record_id"] = [str(uuid.uuid4()) for _ in range(len(df_altered))]
    df_altered["batch_id"] = batch_id
    df_altered["loaded_at"] = batch_timestamp

    # Convert to uppercase
    df_altered.columns = df_altered.columns.str.upper()

    client = get_snowflake_client()

    try:
        conn = client.connect()

        console.print(
            f"[cyan]Loading {len(df_altered):,} rows to ADMOB_DAILY_MIDTEST (BATCH mode)...[/cyan]"
        )

        from snowflake.connector.pandas_tools import write_pandas

        success, nchunks, nrows, _ = write_pandas(
            conn=conn,
            df=df_altered,
            table_name="ADMOB_DAILY_MIDTEST",
            database="DB_T34",
            schema="RAW_MIDTEST",
            auto_create_table=False,
            overwrite=False,
            use_logical_type=True,
        )

        if success:
            console.print(
                f"[green]✓ Loaded {nrows:,} rows (BATCH mode, all loaded_at={batch_timestamp})[/green]"
            )

    except Exception as e:
        console.print(f"[red]✗ Snowflake error: {e}[/red]")
        raise

    finally:
        client.close()


def load_single_row(row, conn, row_num):
    """Load a single row with unique timestamp (for multithreading)."""
    from snowflake.connector.pandas_tools import write_pandas

    row_df = pd.DataFrame([row])
    row_df["raw_record_id"] = str(uuid.uuid4())
    row_df["batch_id"] = None
    row_df["loaded_at"] = pd.Timestamp.now()
    row_df.columns = row_df.columns.str.upper()

    write_pandas(
        conn=conn,
        df=row_df,
        table_name="ADMOB_DAILY_MIDTEST",
        database="DB_T34",
        schema="RAW_MIDTEST",
        auto_create_table=False,
        overwrite=False,
        use_logical_type=True,
    )
    time.sleep(random.uniform(0.1, 0.5))  # Random delay
    return row_num


def load_to_snowflake_realtime(df: pd.DataFrame):
    """Load to Snowflake in realtime mode (10-20 rows, multithreaded, staggered loaded_at)."""
    if df.empty:
        console.print("[yellow]⚠ No data to load[/yellow]")
        return

    # Alter data
    df_altered = alter_data(df)

    # Randomly sample 10-20 rows for realtime demo
    sample_size = random.randint(10, 20)
    df_sample = df_altered.sample(n=min(sample_size, len(df_altered))).copy()

    console.print(
        f"[cyan]Loading {len(df_sample)} rows to ADMOB_DAILY_MIDTEST (REALTIME mode - multithreaded)...[/cyan]"
    )
    console.print(
        f"[dim]Using {len(df_sample)} parallel threads with random delays...[/dim]\n"
    )

    client = get_snowflake_client()

    try:
        conn = client.connect()

        from concurrent.futures import ThreadPoolExecutor, as_completed

        # Load rows in parallel with staggered timestamps
        with ThreadPoolExecutor(max_workers=min(len(df_sample), 10)) as executor:
            futures = []
            for idx, row in df_sample.iterrows():
                futures.append(executor.submit(load_single_row, row, conn, idx))

            for future in as_completed(futures):
                try:
                    row_num = future.result()
                    console.print(f"  [green]✓[/green] Row {row_num} inserted")
                except Exception as e:
                    console.print(f"  [red]✗[/red] Error: {e}")

        console.print(
            f"\n[green]✓ Total loaded: {len(df_sample)} rows (REALTIME mode, staggered loaded_at)[/green]"
        )

    except Exception as e:
        console.print(f"[red]✗ Snowflake error: {e}[/red]")
        raise

    finally:
        client.close()


def main():
    """Main pipeline execution."""
    parser = argparse.ArgumentParser(
        description="AdMob Mid-Course Test Data Collection"
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--batch", action="store_true", help="Batch mode: Same loaded_at"
    )
    group.add_argument(
        "--realtime", action="store_true", help="Realtime mode: Staggered loaded_at"
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
        help="Publisher IDs (default: pub-4738062221647171)",
    )

    args = parser.parse_args()

    mode = "Batch" if args.batch else "Realtime"
    console.print(
        Panel.fit(
            f"[bold cyan]AdMob Mid-Course Test Pipeline[/bold cyan]\n"
            f"Mode: {mode}\n"
            f"Apps: 3 target apps only\n"
            f"Period: Last 7 days\n"
            f"Alterations: ±50% random",
            title="Data Collection",
        )
    )

    # Calculate last 7 days
    end_date = (datetime.now() - timedelta(days=1)).date()
    start_date = end_date - timedelta(days=6)

    console.print(f"\n[cyan]Date range: {start_date} to {end_date}[/cyan]\n")

    all_data = []

    for i, publisher_id in enumerate(args.publishers, 1):
        console.print(
            f"\n[bold cyan]═══ Publisher {i}/{len(args.publishers)}: {publisher_id} ═══[/bold cyan]"
        )

        try:
            # Authenticate
            service = authenticate_admob(publisher_id)

            # Fetch data
            df = fetch_admob_raw(
                service,
                publisher_id,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
            )

            if not df.empty:
                all_data.append(df)

        except Exception as e:
            console.print(f"[red]✗ Publisher {publisher_id} error: {e}[/red]")
            continue

    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        console.print(f"\n[cyan]Total rows: {len(combined_df):,}[/cyan]")

        # Save to CSV
        save_to_csv(combined_df)

        # Load to Snowflake
        if args.batch:
            load_to_snowflake_batch(combined_df)
        else:
            load_to_snowflake_realtime(combined_df)

        console.print(
            Panel.fit(
                f"[bold green]✅ Pipeline Complete[/bold green]\n"
                f"Mode: {mode}\n"
                f"Rows: {len(combined_df):,}\n"
                f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                title="Success",
            )
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
