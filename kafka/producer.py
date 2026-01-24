"""
Fake alerts producer for streaming demo.

Generates random alerts unrelated to batch analytics data.
Sends to Kafka topic 'alerts' every 10 seconds.
"""

import json
import time
import random
import uuid
from datetime import datetime

from kafka import KafkaProducer
from kafka.errors import KafkaError

# Alert configuration
ALERT_TYPES = ["SPEND_SPIKE", "ROAS_DROP", "INSTALL_SURGE", "ERROR_RATE"]
SEVERITIES = ["info", "warning", "critical"]
SEVERITY_WEIGHTS = [0.5, 0.35, 0.15]  # More info, fewer critical

MESSAGES = {
    "SPEND_SPIKE": [
        "Unusual spend pattern detected in {} region",
        "Spend increased 50% in {} market",
        "Budget threshold exceeded in {}",
    ],
    "ROAS_DROP": [
        "ROAS dropped below threshold for {}",
        "Performance degradation detected in {}",
        "ROI alert for {} campaigns",
    ],
    "INSTALL_SURGE": [
        "Install volume spike in {}",
        "Unusual install pattern in {} region",
        "Install rate 3x normal in {}",
    ],
    "ERROR_RATE": [
        "Error rate increased for {} platform",
        "API failures detected in {} region",
        "Service degradation in {}",
    ],
}

REGIONS = ["US", "TH", "VN", "JP", "ID", "BR", "IN", "DE", "GB", "FR"]


def generate_alert() -> dict:
    """Generate a random alert event."""
    alert_type = random.choice(ALERT_TYPES)
    severity = random.choices(SEVERITIES, weights=SEVERITY_WEIGHTS)[0]
    region = random.choice(REGIONS)
    message_template = random.choice(MESSAGES[alert_type])

    return {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "alert_type": alert_type,
        "severity": severity,
        "message": message_template.format(region),
        "region": region,
        "value": round(random.uniform(100, 5000), 2),
    }


def main(batch_count: int = 0, interval: int = 10):
    """
    Main producer loop.

    Args:
        batch_count: If > 0, send this many alerts and exit. If 0, run forever.
        interval: Seconds between alerts (default 10, use 0 for batch mode)
    """
    print("Connecting to Kafka...")

    try:
        producer = KafkaProducer(
            bootstrap_servers='localhost:29092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',
            retries=3,
        )
        print("Connected to Kafka successfully!")
    except KafkaError as e:
        print(f"Failed to connect to Kafka: {e}")
        print("Make sure Kafka is running: docker-compose up -d")
        return

    if batch_count > 0:
        print(f"\nSending {batch_count} alerts in batch mode...")
    else:
        print("\nStarting alert producer (Ctrl+C to stop)...")
    print("-" * 50)

    count = 0
    try:
        while True:
            alert = generate_alert()

            # Send to Kafka
            future = producer.send('alerts', alert)

            # Wait for confirmation
            try:
                future.get(timeout=10)
                count += 1

                # Print with color based on severity
                severity_icon = {
                    "critical": "🔴",
                    "warning": "🟡",
                    "info": "🔵"
                }.get(alert['severity'], "⚪")

                print(f"[{count}] {severity_icon} {alert['severity'].upper():8} | {alert['alert_type']:15} | {alert['message']}")

            except KafkaError as e:
                print(f"Failed to send message: {e}")

            # Check if batch mode is done
            if batch_count > 0 and count >= batch_count:
                print(f"\nBatch complete. Sent {count} alerts.")
                break

            # Wait before next alert
            if interval > 0:
                time.sleep(interval)

    except KeyboardInterrupt:
        print(f"\n\nStopping producer. Sent {count} alerts.")
    finally:
        producer.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Kafka alerts producer")
    parser.add_argument("--batch", "-b", type=int, default=0,
                        help="Send this many alerts and exit (0 = run forever)")
    parser.add_argument("--interval", "-i", type=int, default=10,
                        help="Seconds between alerts (default 10)")

    args = parser.parse_args()
    main(batch_count=args.batch, interval=args.interval)
