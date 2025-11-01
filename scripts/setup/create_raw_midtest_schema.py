#!/usr/bin/env python3
"""
Create RAW_MIDTEST schema and tables for mid-course test demo.

Usage:
    python scripts/setup/create_raw_midtest_schema.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.snowflake_client import get_snowflake_client
from rich.console import Console

console = Console()


def main():
    """Create RAW_MIDTEST schema and tables."""

    client = get_snowflake_client()

    try:
        conn = client.connect()
        cursor = conn.cursor()

        # Create schema
        console.print("[cyan]Creating RAW_MIDTEST schema...[/cyan]")
        cursor.execute("CREATE SCHEMA IF NOT EXISTS RAW_MIDTEST")
        cursor.execute("USE SCHEMA RAW_MIDTEST")
        console.print("[green]✓ Schema created[/green]")

        # Create AdMob table
        console.print("[cyan]Creating ADMOB_DAILY_MIDTEST table...[/cyan]")
        cursor.execute("""
            CREATE OR REPLACE TABLE ADMOB_DAILY_MIDTEST (
                RAW_RECORD_ID VARCHAR(36) NOT NULL,
                BATCH_ID VARCHAR(50),
                DATE VARCHAR(10),
                APP_NAME VARCHAR(255),
                APP_STORE_ID VARCHAR(255),
                COUNTRY_CODE VARCHAR(10),
                PLATFORM VARCHAR(50),
                ESTIMATED_EARNINGS NUMBER(38, 6),
                AD_IMPRESSIONS NUMBER(38, 0),
                AD_CLICKS NUMBER(38, 0),
                AD_REQUESTS NUMBER(38, 0),
                MATCHED_REQUESTS NUMBER(38, 0),
                OBSERVED_ECPM NUMBER(38, 6),
                LOADED_AT TIMESTAMP_NTZ,
                PRIMARY KEY (RAW_RECORD_ID)
            )
        """)
        console.print("[green]✓ ADMOB_DAILY_MIDTEST created[/green]")

        # Create Adjust table
        console.print("[cyan]Creating ADJUST_DAILY_MIDTEST table...[/cyan]")
        cursor.execute("""
            CREATE OR REPLACE TABLE ADJUST_DAILY_MIDTEST (
                RAW_RECORD_ID VARCHAR(36) NOT NULL,
                BATCH_ID VARCHAR(50),
                APP VARCHAR(255),
                STORE_ID VARCHAR(255),
                DAY VARCHAR(10),
                COUNTRY_CODE VARCHAR(10),
                COUNTRY VARCHAR(255),
                OS_NAME VARCHAR(50),
                INSTALLS NUMBER(38, 0),
                CLICKS NUMBER(38, 0),
                DAUS NUMBER(38, 0),
                AD_REVENUE NUMBER(38, 6),
                AD_IMPRESSIONS NUMBER(38, 0),
                NETWORK_COST NUMBER(38, 6),
                LOADED_AT TIMESTAMP_NTZ,
                PRIMARY KEY (RAW_RECORD_ID)
            )
        """)
        console.print("[green]✓ ADJUST_DAILY_MIDTEST created[/green]")

        console.print("\n[bold green]✅ RAW_MIDTEST schema and tables created successfully![/bold green]")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise

    finally:
        client.close()


if __name__ == "__main__":
    sys.exit(main())
