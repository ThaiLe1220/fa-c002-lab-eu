#!/usr/bin/env python3
"""
Create RAW schema tables in Snowflake for mobile analytics pipeline.

Tables:
- RAW.ADMOB_DAILY: AdMob batch data (~13.5K rows/day)
- RAW.ADJUST_HOURLY: Adjust incremental data (~39 rows/hour)
- RAW.ADJUST_COHORTS: Adjust cohort retention data
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import snowflake.connector
from rich.console import Console
from rich.panel import Panel

console = Console()


def get_snowflake_connection():
    """Create Snowflake connection using JWT authentication."""

    # Load private key
    with open('/Users/lehongthai/.snowflake/keys/rsa_key.p8', 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

    pkb = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    return snowflake.connector.connect(
        account='LNB11254',
        user='T34',
        private_key=pkb,
        warehouse='WH_T34',
        database='DB_T34',
        schema='RAW',
        role='RL_T34'
    )


def execute_sql_file(conn, sql_file_path):
    """Execute SQL file and return results."""

    with open(sql_file_path, 'r') as f:
        sql_content = f.read()

    # Remove comments and split by semicolon
    lines = sql_content.split('\n')
    cleaned_lines = []
    for line in lines:
        # Remove line comments
        if '--' in line:
            line = line[:line.index('--')]
        cleaned_lines.append(line)

    cleaned_sql = '\n'.join(cleaned_lines)

    # Split by semicolon
    statements = [s.strip() for s in cleaned_sql.split(';') if s.strip()]

    results = []
    cursor = conn.cursor()

    for i, statement in enumerate(statements, 1):
        # Skip empty or comment-only statements
        if not statement or statement.startswith('/*'):
            continue

        try:
            # Show first 60 chars of statement
            preview = statement[:60].replace('\n', ' ')
            console.print(f"[cyan]Statement {i}: {preview}...[/cyan]")
            cursor.execute(statement)

            # Try to fetch results if it's a SELECT
            if statement.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                results.append(rows)
                console.print(f"[green]✓ Executed ({len(rows)} rows)[/green]")
            else:
                console.print(f"[green]✓ Executed successfully[/green]")

        except Exception as e:
            console.print(f"[red]✗ Error: {str(e)}[/red]")
            # Continue with other statements

    cursor.close()
    return results


def main():
    """Create RAW schema tables."""

    console.print(Panel.fit(
        "[bold cyan]Creating RAW Schema Tables[/bold cyan]\n"
        "Database: DB_T34\n"
        "Schema: RAW\n"
        "Tables: ADMOB_DAILY, ADJUST_HOURLY, ADJUST_COHORTS",
        title="Snowflake Setup"
    ))

    try:
        # Connect to Snowflake
        console.print("\n[cyan]Connecting to Snowflake...[/cyan]")
        conn = get_snowflake_connection()
        console.print("[green]✓ Connected to Snowflake[/green]")

        # Execute SQL file
        sql_file = project_root / 'sql' / 'setup' / 'create_raw_tables.sql'
        console.print(f"\n[cyan]Executing SQL file: {sql_file}[/cyan]")

        results = execute_sql_file(conn, sql_file)

        # Display verification results
        if results and len(results) > 0:
            console.print("\n[bold green]Tables Created Successfully![/bold green]")
            console.print("\n[cyan]Verification Query Results:[/cyan]")
            for row in results[-1]:  # Last result is the verification query
                console.print(f"  • {row}")

        conn.close()

        console.print(Panel.fit(
            "[bold green]✓ RAW Schema Setup Complete[/bold green]\n"
            "Tables ready for data collection pipelines",
            title="Success"
        ))

        return 0

    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
        return 1


if __name__ == '__main__':
    sys.exit(main())
