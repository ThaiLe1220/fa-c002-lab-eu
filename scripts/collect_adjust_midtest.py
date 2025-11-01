#!/usr/bin/env python3
"""
Adjust Data Collection - Mid-Course Test Version

Simplified for demo:
- Only 3 apps
- Last 7 days automatically
- Batch mode: Same loaded_at timestamp
- Realtime mode: Staggered loaded_at timestamps
- Adds UUID for data lineage tracking
- Alters data ±50% randomly before Snowflake load

Usage:
    python scripts/collect_adjust_midtest.py --batch
    python scripts/collect_adjust_midtest.py --realtime
"""

import os
import sys
import argparse
import time
import uuid
import random
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

# Target apps for mid-course test
TARGET_APPS = [
    "video.ai.videogenerator",  # Text to Video FLIX
    "ai.video.generator.text.video",  # AI GPT Generator
    "text.to.video.aivideo.generator",  # Text2Pet
]

# Data directory
MIDTEST_DIR = project_root / "data" / "midtest"
MIDTEST_FILE = MIDTEST_DIR / "adjust_midtest.csv"


def fetch_adjust_daily(api_token: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch daily data from Adjust API for target apps only."""
    console.print(f"[cyan]Fetching Adjust API: {start_date} to {end_date}[/cyan]")

    url = "https://automate.adjust.com/reports-service/csv_report"

    params = {
        "dimensions": "app,store_id,day,country_code,country,os_name",
        "metrics": "installs,clicks,daus,ad_revenue,ad_impressions,network_cost",
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
        return df_filtered

    except Exception as e:
        console.print(f"[red]✗ API error: {e}[/red]")
        return pd.DataFrame()


def alter_data(df: pd.DataFrame) -> pd.DataFrame:
    """Alter numeric data by ±50% randomly (except date/app/country)."""
    df_altered = df.copy()

    numeric_cols = [
        "installs",
        "clicks",
        "daus",
        "ad_revenue",
        "ad_impressions",
        "network_cost",
    ]

    for col in numeric_cols:
        if col in df_altered.columns:
            # Convert to numeric first (handles string values from API)
            df_altered[col] = pd.to_numeric(df_altered[col], errors='coerce')
            # Apply random multiplier between 0.5 and 1.5 (±50%)
            df_altered[col] = df_altered[col].apply(
                lambda x: int(x * random.uniform(0.5, 1.5)) if pd.notna(x) and x != 0 else x
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
            f"[cyan]Loading {len(df_altered):,} rows to ADJUST_DAILY_MIDTEST (BATCH mode)...[/cyan]"
        )

        from snowflake.connector.pandas_tools import write_pandas

        success, nchunks, nrows, _ = write_pandas(
            conn=conn,
            df=df_altered,
            table_name="ADJUST_DAILY_MIDTEST",
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
        table_name="ADJUST_DAILY_MIDTEST",
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
        f"[cyan]Loading {len(df_sample)} rows to ADJUST_DAILY_MIDTEST (REALTIME mode - multithreaded)...[/cyan]"
    )
    console.print(f"[dim]Using {len(df_sample)} parallel threads with random delays...[/dim]\n")

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
    parser = argparse.ArgumentParser(description="Adjust Mid-Course Test Data Collection")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--batch", action="store_true", help="Batch mode: Same loaded_at")
    group.add_argument(
        "--realtime", action="store_true", help="Realtime mode: Staggered loaded_at"
    )

    args = parser.parse_args()

    mode = "Batch" if args.batch else "Realtime"
    console.print(
        Panel.fit(
            f"[bold cyan]Adjust Mid-Course Test Pipeline[/bold cyan]\n"
            f"Mode: {mode}\n"
            f"Apps: 3 target apps only\n"
            f"Period: Last 7 days\n"
            f"Alterations: ±50% random",
            title="Data Collection",
        )
    )

    # Get API token
    api_token = os.getenv("ADJUST_TOKEN")

    if not api_token:
        console.print("[red]✗ Missing ADJUST_TOKEN in .env[/red]")
        return 1

    # Calculate last 7 days
    end_date = (datetime.now() - timedelta(days=1)).date()
    start_date = end_date - timedelta(days=6)

    console.print(f"\n[cyan]Date range: {start_date} to {end_date}[/cyan]\n")

    try:
        # Fetch data
        df = fetch_adjust_daily(
            api_token, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
        )

        if not df.empty:
            console.print(f"\n[cyan]Total rows: {len(df):,}[/cyan]")

            # Save to CSV
            save_to_csv(df)

            # Load to Snowflake
            if args.batch:
                load_to_snowflake_batch(df)
            else:
                load_to_snowflake_realtime(df)

            console.print(
                Panel.fit(
                    f"[bold green]✅ Pipeline Complete[/bold green]\n"
                    f"Mode: {mode}\n"
                    f"Rows: {len(df):,}\n"
                    f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    title="Success",
                )
            )

        return 0

    except Exception as e:
        console.print(f"\n[bold red]✗ Pipeline failed: {e}[/bold red]")
        import traceback

        console.print(f"[red]{traceback.format_exc()}[/red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
