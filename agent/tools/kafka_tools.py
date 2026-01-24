"""
Streaming alerts tool - queries PostgreSQL sink.

This tool allows the agent to query real-time alerts
from the streaming pipeline (Kafka → PostgreSQL).

The alerts are UNRELATED to batch analytics data.
"""

import psycopg2
from typing import Annotated
from langchain_core.tools import tool

# PostgreSQL configuration (matches kafka/docker-compose.yml)
PG_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "database": "streaming",
    "user": "capstone",
    "password": "capstone123",
}


def get_streaming_db():
    """Connect to streaming PostgreSQL database."""
    return psycopg2.connect(**PG_CONFIG)


@tool
def query_realtime_alerts(
    severity: Annotated[str, "Filter by severity: 'all', 'critical', 'warning', or 'info'"] = "all",
    limit: Annotated[int, "Number of alerts to return (max 20)"] = 10
) -> str:
    """
    Query real-time alerts from the streaming pipeline.

    Use this tool when asked about:
    - Recent alerts or notifications
    - Real-time monitoring events
    - Critical/warning alerts
    - Streaming data status
    - "Any alerts?" or "Show me alerts"

    The streaming pipeline is SEPARATE from batch analytics (Snowflake).
    It shows alerts like:
    - SPEND_SPIKE: Unusual spending patterns
    - ROAS_DROP: Return on ad spend decreased
    - INSTALL_SURGE: Unusual install volume
    - ERROR_RATE: System errors detected

    Args:
        severity: Filter by alert severity ('all', 'critical', 'warning', 'info')
        limit: Maximum number of alerts to return (default 10, max 20)

    Returns:
        Recent alerts from the streaming pipeline
    """
    # Cap limit at 20
    limit = min(limit, 20)

    try:
        conn = get_streaming_db()
        cur = conn.cursor()

        if severity == "all":
            cur.execute("""
                SELECT timestamp, alert_type, severity, message, region, value
                FROM alerts
                ORDER BY created_at DESC
                LIMIT %s
            """, (limit,))
        else:
            cur.execute("""
                SELECT timestamp, alert_type, severity, message, region, value
                FROM alerts
                WHERE severity = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (severity, limit))

        rows = cur.fetchall()

        # Also get summary counts
        cur.execute("""
            SELECT severity, COUNT(*)
            FROM alerts
            WHERE created_at > NOW() - INTERVAL '1 hour'
            GROUP BY severity
        """)
        counts = dict(cur.fetchall())

        cur.close()
        conn.close()

        if not rows:
            if severity == "all":
                return "No alerts found. The streaming pipeline may not be running.\n\nTo start it:\n1. cd kafka && docker-compose up -d\n2. uv run python consumer.py\n3. uv run python producer.py"
            else:
                return f"No {severity} alerts found in the last hour."

        # Format output
        output = f"**Real-time Alerts** (showing {len(rows)} of {sum(counts.values()) if counts else len(rows)} in last hour)\n\n"

        # Summary
        if counts:
            output += "**Summary (last hour):** "
            summary_parts = []
            if counts.get('critical', 0) > 0:
                summary_parts.append(f"🔴 {counts['critical']} critical")
            if counts.get('warning', 0) > 0:
                summary_parts.append(f"🟡 {counts['warning']} warning")
            if counts.get('info', 0) > 0:
                summary_parts.append(f"🔵 {counts['info']} info")
            output += ", ".join(summary_parts) + "\n\n"

        output += "---\n\n"

        for row in rows:
            ts, alert_type, sev, msg, region, val = row
            icon = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(sev, "⚪")

            output += f"{icon} **{sev.upper()}** | {alert_type}\n"
            output += f"   {msg}\n"
            if region and val:
                output += f"   Region: {region} | Value: ${val:,.2f}\n"
            output += f"   _{ts.strftime('%Y-%m-%d %H:%M:%S')}_\n\n"

        return output

    except psycopg2.OperationalError as e:
        return f"Cannot connect to streaming database. Is the pipeline running?\n\nError: {str(e)}\n\nTo start:\n1. cd kafka && docker-compose up -d\n2. uv run python consumer.py"

    except Exception as e:
        return f"Error querying alerts: {str(e)}"


# Test function
if __name__ == "__main__":
    print("Testing query_realtime_alerts tool...\n")

    # Test all alerts
    print("=== All Alerts ===")
    result = query_realtime_alerts.invoke({"severity": "all", "limit": 5})
    print(result)

    print("\n=== Critical Only ===")
    result = query_realtime_alerts.invoke({"severity": "critical", "limit": 5})
    print(result)
