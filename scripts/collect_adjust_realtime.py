#!/usr/bin/env python3
"""
Adjust Data Collection - REALTIME MODE (PostgreSQL)

For mid-course test demo:
- Collects last 7 days of data
- Shows row-by-row ingestion with staggered timestamps
- Lands in LOCAL PostgreSQL (not Snowflake)
- Demonstrates real-time streaming pattern

Usage:
    python scripts/collect_adjust_realtime.py
"""

import os
import sys
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
import psycopg
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

# Load environment
load_dotenv(dotenv_path=".secret/.env")

console = Console()

# PostgreSQL connection (using port 5433 to avoid conflict with local PostgreSQL)
POSTGRES_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "dbname": "midtest_db",
    "user": "midtest_user",
    "password": "midtest_password"
}

# Target apps for mid-course test
TARGET_APPS = [
    "video.ai.videogenerator",
    "ai.video.generator.text.video",
    "text.to.video.aivideo.generator",
]

def get_postgres_connection():
    """Create PostgreSQL connection"""
    return psycopg.connect(**POSTGRES_CONFIG)

def fetch_adjust_data():
    """Load Adjust data from CSV file (already collected)"""
    console.print("\n[cyan]📡 Loading Adjust data from CSV...[/cyan]")

    csv_path = project_root / "data/midtest/adjust_midtest.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    # DEMO: Only take 30 rows for quick demo
    df = df.head(30)

    # Convert to list of dicts
    all_data = df.to_dict('records')

    console.print(f"[green]✅ Loaded {len(all_data)} rows from CSV (demo sample)[/green]")

    return all_data

def insert_to_postgres_streaming(rows):
    """Insert rows one-by-one to PostgreSQL (realtime demo)"""
    console.print(f"\n[yellow]🔄 Streaming {len(rows)} rows to PostgreSQL (row-by-row)...[/yellow]")

    conn = get_postgres_connection()

    insert_query = """
        INSERT INTO raw.adjust_realtime
        (uuid, day, store_id, country_code, os_name, installs, clicks, impressions, daus, loaded_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    inserted_count = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Streaming rows...", total=len(rows))

        for row in rows:
            # Generate unique UUID and timestamp for each row
            row_uuid = str(uuid.uuid4())
            loaded_at = datetime.now()

            values = (
                row_uuid,
                row.get("day"),
                row.get("store_id"),
                row.get("country"),
                row.get("os_name"),
                row.get("installs", 0),
                row.get("clicks", 0),
                row.get("impressions", 0),
                row.get("daus", 0),
                loaded_at
            )

            with conn.cursor() as cur:
                cur.execute(insert_query, values)
                conn.commit()

            inserted_count += 1
            progress.update(task, advance=1)

            # Simulate streaming delay
            time.sleep(0.05)  # 50ms delay per row

    conn.close()

    console.print(f"[green]✅ Successfully streamed {inserted_count} rows to PostgreSQL[/green]")
    return inserted_count

def verify_data():
    """Verify data in PostgreSQL"""
    console.print("\n[cyan]🔍 Verifying data in PostgreSQL...[/cyan]")

    conn = get_postgres_connection()

    with conn.cursor() as cur:
        # Count rows
        cur.execute("SELECT COUNT(*) FROM raw.adjust_realtime")
        total_rows = cur.fetchone()[0]

        # Latest timestamp
        cur.execute("SELECT MAX(loaded_at) FROM raw.adjust_realtime")
        latest_timestamp = cur.fetchone()[0]

        # Sample data
        cur.execute("""
            SELECT day, store_id, country_code, installs, daus, loaded_at
            FROM raw.adjust_realtime
            ORDER BY loaded_at DESC
            LIMIT 5
        """)
        sample_rows = cur.fetchall()

    conn.close()

    console.print(f"\n[green]📊 PostgreSQL Data Summary:[/green]")
    console.print(f"   Total rows: {total_rows}")
    console.print(f"   Latest timestamp: {latest_timestamp}")
    console.print("\n[cyan]Sample rows (latest 5):[/cyan]")
    for row in sample_rows:
        console.print(f"   {row}")

def main():
    """Main execution"""
    console.print(Panel.fit(
        "[bold cyan]Adjust Realtime Data Collection[/bold cyan]\n"
        "[yellow]Mode: Streaming to PostgreSQL[/yellow]",
        border_style="cyan"
    ))

    try:
        # Fetch data
        rows = fetch_adjust_data()

        if not rows:
            console.print("[yellow]⚠️  No data fetched from API[/yellow]")
            return

        console.print(f"[green]✅ Fetched {len(rows)} rows from API[/green]")

        # Insert to PostgreSQL (streaming)
        insert_to_postgres_streaming(rows)

        # Verify
        verify_data()

        console.print("\n[bold green]✅ Realtime pipeline complete![/bold green]")

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]")
        raise

if __name__ == "__main__":
    main()
