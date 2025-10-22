#!/usr/bin/env python3
"""
AdMob Batch Data Collection Pipeline

Fetches daily ad performance data from AdMob API and loads to Snowflake.

Pattern: Following M01W03 lab structure for batch pipeline
Volume: ~13,500 rows per day
Demo: Load 7 days = 94,000 rows

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
from rich.progress import track
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
            console.print(f"[cyan]✓ Refreshed credentials for {publisher_id}[/cyan]")

        service = build("admob", "v1", credentials=credentials)
        console.print(f"[green]✓ Authenticated: {publisher_id}[/green]")
        return service

    except Exception as e:
        raise RuntimeError(f"AdMob authentication failed: {str(e)}")


def fetch_admob_data(
    service,
    publisher_id: str,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """
    Fetch AdMob data for date range.

    Args:
        service: AdMob API service
        publisher_id: Publisher ID
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        pandas DataFrame with ad performance data
    """

    # Build request (following validated API structure - snake_case)
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
        # Execute API request
        response = (
            service.accounts()
            .mediationReport()
            .generate(parent=f"accounts/{publisher_id}", body=request_body)
            .execute()
        )

        # Parse response (can be list or dict)
        rows = []

        if isinstance(response, list):
            # Response is a list of row items
            for item in response:
                if "row" in item:
                    row = item["row"]

                    # Extract dimensions
                    dim_values = row.get("dimensionValues", {})

                    # Extract metrics
                    metric_values = row.get("metricValues", {})

                    rows.append({
                        "date": dim_values.get("DATE", {}).get("value"),
                        "app_id": dim_values.get("APP", {}).get("displayLabel", ""),
                        "country_code": dim_values.get("COUNTRY", {}).get("value", ""),
                        "platform": dim_values.get("PLATFORM", {}).get("value", ""),
                        "ad_format": dim_values.get("FORMAT", {}).get("value", ""),
                        "ad_unit_id": dim_values.get("AD_UNIT", {}).get("displayLabel", ""),
                        "ad_impressions": int(metric_values.get("IMPRESSIONS", {}).get("integerValue", 0)),
                        "ad_clicks": int(metric_values.get("CLICKS", {}).get("integerValue", 0)),
                        "ad_requests": int(metric_values.get("AD_REQUESTS", {}).get("integerValue", 0)),
                        "matched_requests": int(metric_values.get("MATCHED_REQUESTS", {}).get("integerValue", 0)),
                        "estimated_earnings": float(metric_values.get("ESTIMATED_EARNINGS", {}).get("microsValue", 0)) / 1_000_000,
                        "observed_ecpm": float(metric_values.get("OBSERVED_ECPM", {}).get("microsValue", 0)) / 1_000_000,
                    })
        else:
            # Response is a dict with 'row' key
            if "row" in response:
                for row in response["row"]:
                    # Extract dimensions
                    dim_values = row.get("dimensionValues", {})

                    # Extract metrics
                    metric_values = row.get("metricValues", {})

                    rows.append({
                        "date": dim_values.get("DATE", {}).get("value"),
                        "app_id": dim_values.get("APP", {}).get("displayLabel", ""),
                        "country_code": dim_values.get("COUNTRY", {}).get("value", ""),
                        "platform": dim_values.get("PLATFORM", {}).get("value", ""),
                        "ad_format": dim_values.get("FORMAT", {}).get("value", ""),
                        "ad_unit_id": dim_values.get("AD_UNIT", {}).get("displayLabel", ""),
                        "ad_impressions": int(metric_values.get("IMPRESSIONS", {}).get("integerValue", 0)),
                        "ad_clicks": int(metric_values.get("CLICKS", {}).get("integerValue", 0)),
                        "ad_requests": int(metric_values.get("AD_REQUESTS", {}).get("integerValue", 0)),
                        "matched_requests": int(metric_values.get("MATCHED_REQUESTS", {}).get("integerValue", 0)),
                        "estimated_earnings": float(metric_values.get("ESTIMATED_EARNINGS", {}).get("microsValue", 0)) / 1_000_000,
                        "observed_ecpm": float(metric_values.get("OBSERVED_ECPM", {}).get("microsValue", 0)) / 1_000_000,
                    })

        df = pd.DataFrame(rows)

        if not df.empty:
            # Convert date column to proper format (DATE only, not timestamp)
            df['date'] = pd.to_datetime(df['date']).dt.date

            # Add metadata
            df['loaded_at'] = pd.Timestamp.now()
            df['batch_id'] = f"{start_date}_{end_date}"

            # Rename columns to match Snowflake table schema (uppercase)
            df.columns = df.columns.str.upper()

        return df

    except Exception as e:
        raise RuntimeError(f"API request failed: {str(e)}")


def main():
    """Main execution: Fetch AdMob data and load to Snowflake."""

    parser = argparse.ArgumentParser(description='Collect AdMob batch data')
    parser.add_argument('--days', type=int, default=7, help='Number of days to fetch (default: 7)')
    parser.add_argument('--publisher', type=str, default='pub-4738062221647171', help='Publisher ID')
    args = parser.parse_args()

    console.print(Panel.fit(
        f"[bold cyan]AdMob Batch Data Collection[/bold cyan]\n"
        f"Publisher: {args.publisher}\n"
        f"Days: {args.days}\n"
        f"Target: Snowflake RAW.ADMOB_DAILY",
        title="Pipeline Start"
    ))

    try:
        # Authenticate
        console.print("\n[cyan]Step 1: Authenticating...[/cyan]")
        service = authenticate_admob(args.publisher)

        # Fetch data for each day (start from 3 days ago to allow for AdMob data finalization)
        console.print(f"\n[cyan]Step 2: Fetching {args.days} days of data...[/cyan]")

        all_data = []
        start_offset = 3  # Start from 3 days ago
        for i in track(range(args.days), description="Fetching batches"):
            target_date = (datetime.now() - timedelta(days=i+start_offset)).strftime("%Y-%m-%d")

            df = fetch_admob_data(
                service,
                args.publisher,
                target_date,
                target_date
            )

            if not df.empty:
                all_data.append(df)
                console.print(f"  ✓ {target_date}: {len(df):,} rows")
            else:
                console.print(f"  ⚠ {target_date}: No data")

        if not all_data:
            console.print("[yellow]⚠ No data fetched[/yellow]")
            return 1

        # Combine all batches
        combined_df = pd.concat(all_data, ignore_index=True)
        console.print(f"\n[green]✓ Total rows fetched: {len(combined_df):,}[/green]")

        # Load to Snowflake
        console.print("\n[cyan]Step 3: Loading to Snowflake...[/cyan]")

        with get_snowflake_client() as sf:
            rows_loaded = sf.load_dataframe(
                df=combined_df,
                table_name='ADMOB_DAILY'
            )

        console.print(Panel.fit(
            f"[bold green]✓ Pipeline Complete[/bold green]\n"
            f"Rows loaded: {rows_loaded:,}\n"
            f"Table: RAW.ADMOB_DAILY",
            title="Success"
        ))

        return 0

    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
        return 1


if __name__ == '__main__':
    sys.exit(main())
