#!/usr/bin/env python3
"""
Quick Data Verification Script

Check what data exists in Snowflake without running collection pipelines.

Usage:
    python scripts/check_data.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.snowflake_client import get_snowflake_client
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def check_snowflake_data():
    """Check what data exists in Snowflake."""

    console.print(
        Panel.fit(
            "[bold cyan]Snowflake Data Verification[/bold cyan]\n"
            "Database: DB_T34\n"
            "Schema: RAW",
            title="Data Check",
        )
    )

    client = get_snowflake_client()

    try:
        conn = client.connect()
        cursor = conn.cursor()

        # 1. List all tables in RAW schema
        console.print("\n[cyan]📊 Tables in RAW schema:[/cyan]")
        cursor.execute(
            """
            SELECT TABLE_NAME, ROW_COUNT, BYTES
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = 'RAW'
            AND TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """
        )

        tables = cursor.fetchall()

        if not tables:
            console.print("[yellow]⚠️  No tables found in RAW schema[/yellow]")
            return

        # Display tables
        table_list = Table(title="Available Tables")
        table_list.add_column("Table Name", style="cyan")
        table_list.add_column("Rows", justify="right", style="green")
        table_list.add_column("Size (MB)", justify="right", style="yellow")

        for table_name, row_count, bytes_size in tables:
            size_mb = f"{bytes_size / 1024 / 1024:.2f}" if bytes_size else "0"
            table_list.add_row(table_name, str(row_count or 0), size_mb)

        console.print(table_list)

        # 2. Check each table for data samples
        for table_name, _, _ in tables:
            console.print(f"\n[cyan]🔍 Sample data from {table_name}:[/cyan]")

            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM RAW.{table_name}")
            count = cursor.fetchone()[0]

            # Get date range if DATE/DAY column exists
            cursor.execute(
                f"""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = 'RAW'
                AND TABLE_NAME = '{table_name}'
                AND COLUMN_NAME IN ('DATE', 'DAY', 'EVENT_DATE', 'CREATED_AT', 'DATE_KEY')
            """
            )
            date_col = cursor.fetchone()

            if date_col:
                date_col_name = date_col[0]
                cursor.execute(
                    f"""
                    SELECT MIN({date_col_name}), MAX({date_col_name})
                    FROM RAW.{table_name}
                """
                )
                min_date, max_date = cursor.fetchone()
                console.print(f"  • Total rows: {count:,}")
                console.print(f"  • Date range: {min_date} → {max_date}")
            else:
                console.print(f"  • Total rows: {count:,}")

            # Show random sample rows - select specific columns to avoid timestamp conversion issues
            try:
                # Get column names excluding LOADED_AT
                cursor.execute(
                    f"""
                    SELECT COLUMN_NAME
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = 'RAW'
                    AND TABLE_NAME = '{table_name}'
                    AND COLUMN_NAME NOT IN ('LOADED_AT', 'BATCH_ID')
                    ORDER BY ORDINAL_POSITION
                """
                )
                cols = [row[0] for row in cursor.fetchall()]

                if cols:
                    col_list = ", ".join(cols[:10])  # First 10 columns
                    cursor.execute(
                        f"SELECT {col_list} FROM RAW.{table_name} ORDER BY RANDOM() LIMIT 3"
                    )
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()

                    if rows:
                        console.print(f"\n  [bold]Random Sample Rows:[/bold]")
                        for i, row in enumerate(rows, 1):
                            console.print(f"\n  [cyan]Row {i}:[/cyan]")
                            for col, val in zip(columns, row):
                                val_str = str(val)[:60] if val is not None else "None"
                                console.print(f"    {col}: {val_str}")
            except Exception as sample_error:
                console.print(
                    f"  [yellow]⚠️  Could not display sample rows: {str(sample_error)[:80]}[/yellow]"
                )
                console.print(
                    f"  [cyan]💡 Data exists and is queryable in Snowflake UI[/cyan]"
                )

            console.print()

        # 3. Summary
        console.print(
            Panel.fit(
                f"[green]✓ Found {len(tables)} table(s) in RAW schema[/green]\n"
                f"[cyan]Ready for dbt transformations[/cyan]",
                title="Status",
            )
        )

    except Exception as e:
        console.print(f"[red]❌ Error: {str(e)}[/red]")
        raise

    finally:
        client.close()


if __name__ == "__main__":
    check_snowflake_data()
