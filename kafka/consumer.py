"""
Alert consumer - reads from Kafka and writes to PostgreSQL.

This creates the streaming sink that the agent tool will query.
"""

import json
import psycopg2
from psycopg2.extras import execute_values
from kafka import KafkaConsumer
from kafka.errors import KafkaError

# PostgreSQL configuration (matches docker-compose.yml)
PG_CONFIG = {
    "host": "localhost",
    "port": 5433,  # Using 5433 to avoid conflicts
    "database": "streaming",
    "user": "capstone",
    "password": "capstone123",
}


def get_db_connection():
    """Create PostgreSQL connection."""
    return psycopg2.connect(**PG_CONFIG)


def create_table(conn):
    """Create alerts table if not exists."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id UUID PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                alert_type VARCHAR(50) NOT NULL,
                severity VARCHAR(20) NOT NULL,
                message TEXT NOT NULL,
                region VARCHAR(10),
                value DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT NOW()
            );

            -- Index for faster queries by severity and time
            CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
            CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at DESC);
        """)
        conn.commit()
    print("✅ Alerts table ready")


def main():
    """Main consumer loop."""
    print("Connecting to PostgreSQL...")

    try:
        conn = get_db_connection()
        create_table(conn)
    except psycopg2.Error as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        print("Make sure PostgreSQL is running: docker-compose up -d")
        return

    print("Connecting to Kafka...")

    try:
        consumer = KafkaConsumer(
            'alerts',
            bootstrap_servers='localhost:29092',
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='alert-consumer-group',
            consumer_timeout_ms=30000,  # 30 second timeout (for batch processing)
        )
        print("✅ Connected to Kafka successfully!")
    except KafkaError as e:
        print(f"❌ Failed to connect to Kafka: {e}")
        print("Make sure Kafka is running: docker-compose up -d")
        conn.close()
        return

    print("\nConsuming alerts (Ctrl+C to stop)...")
    print("-" * 50)

    count = 0
    try:
        for message in consumer:
            alert = message.value

            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO alerts (id, timestamp, alert_type, severity, message, region, value)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                    """, (
                        alert['id'],
                        alert['timestamp'],
                        alert['alert_type'],
                        alert['severity'],
                        alert['message'],
                        alert.get('region'),
                        alert.get('value'),
                    ))
                    conn.commit()

                count += 1

                # Print with color based on severity
                severity_icon = {
                    "critical": "🔴",
                    "warning": "🟡",
                    "info": "🔵"
                }.get(alert['severity'], "⚪")

                print(f"[{count}] {severity_icon} Stored: {alert['alert_type']} - {alert['message'][:50]}")

            except psycopg2.Error as e:
                print(f"❌ Database error: {e}")
                conn.rollback()

    except KeyboardInterrupt:
        print(f"\n\nStopping consumer. Processed {count} alerts.")
    finally:
        consumer.close()
        conn.close()


if __name__ == "__main__":
    main()
