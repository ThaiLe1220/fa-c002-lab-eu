"""
Snowflake client utilities for mobile analytics pipeline.

Provides reusable connection and data loading functions following
M01W03 lab pattern.
"""

from typing import Optional
import pandas as pd
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from rich.console import Console

console = Console()


class SnowflakeClient:
    """Snowflake connection manager with data loading utilities."""

    def __init__(
        self,
        account: str = "LNB11254",
        user: str = "T34",
        warehouse: str = "WH_T34",
        database: str = "DB_T34",
        schema: str = "RAW",
        role: str = "RL_T34",
        private_key_path: str = "/Users/lehongthai/.snowflake/keys/rsa_key.p8",
    ):
        """Initialize Snowflake client with JWT authentication."""

        self.account = account
        self.user = user
        self.warehouse = warehouse
        self.database = database
        self.schema = schema
        self.role = role
        self.private_key_path = private_key_path
        self.connection = None

    def connect(self):
        """Create Snowflake connection using JWT authentication."""

        if self.connection is not None:
            return self.connection

        # Load private key
        with open(self.private_key_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(), password=None, backend=default_backend()
            )

        pkb = private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        self.connection = snowflake.connector.connect(
            account=self.account,
            user=self.user,
            private_key=pkb,
            warehouse=self.warehouse,
            database=self.database,
            schema=self.schema,
            role=self.role,
        )

        console.print(
            f"[green]✓ Connected to Snowflake: {self.database}.{self.schema}[/green]"
        )
        return self.connection

    def close(self):
        """Close Snowflake connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            console.print("[cyan]✓ Snowflake connection closed[/cyan]")

    def load_dataframe(
        self,
        df: pd.DataFrame,
        table_name: str,
        chunk_size: int = 16000,
        auto_create_table: bool = False,
    ) -> int:
        """
        Load pandas DataFrame to Snowflake table.

        Args:
            df: pandas DataFrame to load
            table_name: Target table name (without schema)
            chunk_size: Rows per chunk for upload
            auto_create_table: Whether to create table if not exists

        Returns:
            Number of rows loaded
        """

        if not self.connection:
            self.connect()

        # Show data preview
        console.print(f"\n[cyan]Loading to {self.schema}.{table_name}:[/cyan]")
        console.print(f"  Rows: {len(df):,}")
        console.print(f"  Columns: {len(df.columns)}")

        try:
            # Use Snowflake's write_pandas for efficient bulk loading
            success, nchunks, nrows, _ = write_pandas(
                conn=self.connection,
                df=df,
                table_name=table_name,
                schema=self.schema,
                database=self.database,
                chunk_size=chunk_size,
                auto_create_table=auto_create_table,
                overwrite=False,  # Append mode
                use_logical_type=True,  # Fix datetime handling
            )

            if success:
                console.print(
                    f"[green]✓ Loaded {nrows:,} rows in {nchunks} chunks[/green]"
                )
                return nrows
            else:
                console.print("[red]✗ Load failed[/red]")
                return 0

        except Exception as e:
            console.print(f"[red]✗ Error loading data: {str(e)}[/red]")
            raise

    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute SQL query and return results as DataFrame.

        Args:
            query: SQL query to execute

        Returns:
            pandas DataFrame with query results
        """

        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            df = cursor.fetch_pandas_all()
            return df
        finally:
            cursor.close()

    def get_table_row_count(self, table_name: str) -> int:
        """Get row count for a table."""

        query = f"SELECT COUNT(*) as count FROM {self.schema}.{table_name}"
        df = self.execute_query(query)
        return int(df["COUNT"].iloc[0])

    def get_latest_timestamp(
        self, table_name: str, timestamp_column: str = "loaded_at"
    ) -> Optional[pd.Timestamp]:
        """
        Get latest timestamp from table for incremental loading.

        Args:
            table_name: Table to query
            timestamp_column: Timestamp column name

        Returns:
            Latest timestamp or None if table is empty
        """

        query = f"""
        SELECT MAX({timestamp_column}) as max_ts
        FROM {self.schema}.{table_name}
        """

        try:
            df = self.execute_query(query)
            max_ts = df["MAX_TS"].iloc[0]
            return pd.to_datetime(max_ts) if max_ts else None
        except Exception:
            return None

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Convenience function for quick connections
def get_snowflake_client(**kwargs) -> SnowflakeClient:
    """
    Get Snowflake client with default configuration.

    Returns:
        SnowflakeClient instance
    """
    return SnowflakeClient(**kwargs)
