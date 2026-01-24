"""
Test Kafka and PostgreSQL connectivity.

Run this after docker-compose up to verify everything works.
"""

import sys


def test_kafka():
    """Test Kafka connection."""
    print("🔍 Testing Kafka connection...")

    try:
        from kafka import KafkaAdminClient
        from kafka.errors import KafkaError

        admin = KafkaAdminClient(
            bootstrap_servers='localhost:29092',
            client_id='test-client'
        )

        # List topics (will be empty initially)
        topics = admin.list_topics()
        print(f"✅ Kafka: Ready (topics: {topics if topics else 'none yet'})")
        admin.close()
        return True

    except Exception as e:
        print(f"❌ Kafka: Failed - {e}")
        return False


def test_postgres():
    """Test PostgreSQL connection."""
    print("🔍 Testing PostgreSQL connection...")

    try:
        import psycopg2

        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            database="streaming",
            user="capstone",
            password="capstone123"
        )

        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"✅ PostgreSQL: Ready ({version[:30]}...)")

        cur.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ PostgreSQL: Failed - {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("Streaming Pipeline Connection Test")
    print("=" * 50)
    print()

    kafka_ok = test_kafka()
    postgres_ok = test_postgres()

    print()
    print("-" * 50)

    if kafka_ok and postgres_ok:
        print("🎉 All systems ready! You can now run:")
        print("   Terminal 1: uv run python consumer.py")
        print("   Terminal 2: uv run python producer.py")
        return 0
    else:
        print("⚠️  Some services are not ready.")
        print("   Run: docker-compose up -d")
        print("   Wait 30 seconds, then try again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
