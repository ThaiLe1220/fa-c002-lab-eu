#!/usr/bin/env python3
"""
AdMob Daily Data Collection - Pure RAW Pipeline

Fetches daily ad performance data from AdMob API and loads to Snowflake RAW table.
NO TRANSFORMATIONS - stores exact API response (flattened).

Usage:
    python scripts/collect_admob.py --days 7
"""

import os
import sys
import pickle
import argparse
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


def fetch_admob_raw(
    service,
    publisher_id: str,
    start_date: str,
    end_date: str
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

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    request_body = {
        "report_spec": {
            "date_range": {
                "start_date": {
                    "year": start_dt.year,
                    "month": start_dt.month,
                    "day": start_dt.day
                },
                "end_date": {
                    "year": end_dt.year,
                    "month": end_dt.month,
                    "day": end_dt.day
                }
            },
            "dimensions": ["APP", "DATE", "COUNTRY", "PLATFORM", "FORMAT", "AD_UNIT"],
            "metrics": [
                "ESTIMATED_EARNINGS",
                "IMPRESSIONS",
                "CLICKS",
                "AD_REQUESTS",
                "MATCHED_REQUESTS",
                "OBSERVED_ECPM"
            ],
            "localization_settings": {"currency_code": "USD"}
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

                    # Extract raw values (keep as strings, no conversions)
                    rows.append({
                        "date": dim.get("DATE", {}).get("value"),
                        "app_id": dim.get("APP", {}).get("displayLabel"),
                        "country_code": dim.get("COUNTRY", {}).get("value"),
                        "platform": dim.get("PLATFORM", {}).get("value"),
                        "ad_format": dim.get("FORMAT", {}).get("value"),
                        "ad_unit_id": dim.get("AD_UNIT", {}).get("displayLabel"),
                        "ad_impressions": met.get("IMPRESSIONS", {}).get("integerValue"),
                        "ad_clicks": met.get("CLICKS", {}).get("integerValue"),
                        "ad_requests": met.get("AD_REQUESTS", {}).get("integerValue"),
                        "matched_requests": met.get("MATCHED_REQUESTS", {}).get("integerValue"),
                        "estimated_earnings": met.get("ESTIMATED_EARNINGS", {}).get("microsValue"),
                        "observed_ecpm": met.get("OBSERVED_ECPM", {}).get("microsValue"),
                    })

        df = pd.DataFrame(rows)

        if not df.empty:
            # Add metadata
            df["loaded_at"] = datetime.now()
            df["batch_id"] = f"{start_date}_{end_date}"

            # Convert column names to UPPERCASE (Snowflake convention)
            df.columns = df.columns.str.upper()

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
            overwrite=False
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


def main():
    """Main pipeline execution."""

    parser = argparse.ArgumentParser(description="AdMob Daily RAW Data Collection")
    parser.add_argument("--days", type=int, default=7, help="Number of days to fetch (default: 7)")
    parser.add_argument("--publisher", type=str, default="pub-4738062221647171", help="Publisher ID")
    args = parser.parse_args()

    console.print(Panel.fit(
        "[bold cyan]AdMob RAW Pipeline[/bold cyan]\n"
        f"Fetching last {args.days} day(s)\n"
        "Mode: Pure RAW (no transformations)",
        title="Data Collection"
    ))

    try:
        # Authenticate
        console.print("\n[bold]Step 1: Authenticate[/bold]")
        service = authenticate_admob(args.publisher)

        # Fetch data (start from 3 days ago - AdMob data finalization delay)
        console.print("\n[bold]Step 2: Fetch from AdMob API[/bold]")

        all_data = []
        start_offset = 3

        for i in range(args.days):
            target_date = (datetime.now() - timedelta(days=i+start_offset)).date()
            date_str = target_date.strftime("%Y-%m-%d")

            df = fetch_admob_raw(service, args.publisher, date_str, date_str)

            if not df.empty:
                all_data.append(df)
                console.print(f"  ✓ {date_str}: {len(df):,} rows")
            else:
                console.print(f"  ⚠ {date_str}: No data")

        if not all_data:
            console.print("[yellow]⚠ No data fetched[/yellow]")
            return 0

        # Combine all batches
        combined_df = pd.concat(all_data, ignore_index=True)
        console.print(f"\n[green]✓ Total rows: {len(combined_df):,}[/green]")

        # Load to Snowflake (no transformations)
        console.print("\n[bold]Step 3: Load to Snowflake RAW[/bold]")
        load_to_snowflake(combined_df)

        # Success
        console.print(Panel.fit(
            f"[bold green]✓ Pipeline Complete[/bold green]\n"
            f"Days: {args.days}\n"
            f"Rows Loaded: {len(combined_df):,}\n"
            f"Loaded At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            title="Success"
        ))

        return 0

    except Exception as e:
        console.print(f"\n[bold red]✗ Pipeline failed: {e}[/bold red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
