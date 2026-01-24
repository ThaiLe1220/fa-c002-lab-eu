# Implementation Priority Guide

**Definitive execution order with reasoning. Read this before coding.**

**Created:** January 24, 2026
**Deadline:** January 24, 2026 (DEMO DAY)
**Current Score:** ~55 pts
**Target Score:** 85+ pts

---

## Executive Summary

### The Reality Check

| Category | What We Have | What's Missing | Impact |
|----------|--------------|----------------|--------|
| **Core (60 pts)** | ~35 pts | Kafka, Airflow, RAG | -25 pts |
| **Extra (40 pts)** | ~20 pts | Documentation of features | -20 pts |

**Critical insight:** Without the 3 checkboxes (Kafka, Airflow, RAG), we CANNOT get full core points. These are **blocking requirements**, not nice-to-haves.

### The Priority Order

```
MUST DO (Core Points - Blocking)
================================
1. Kafka Setup      → 30-45 min → Unblocks 7.5 pts
2. Airflow Setup    → 30-45 min → Unblocks 7.5 pts
3. Basic RAG        → 45-60 min → Unblocks 10 pts
4. Kafka Agent Tool → 15 min    → Unblocks 5 pts

SHOULD DO (Extra Points - Quick Wins)
=====================================
5. dbt Macros       → 30 min    → 10-15 pts
6. dbt-expectations → 30 min    → 10-15 pts
7. Enhanced Prompts → 20 min    → 5-10 pts (document existing)

NICE TO HAVE (Extra Points - High Effort)
=========================================
8. Hybrid RAG       → 1-2 hrs   → 15-20 pts
9. Multi-Model      → 2-3 hrs   → 15-20 pts
10. Error Handling  → 1 hr      → 10 pts
```

---

## Phase 1: Core Checkboxes (MUST DO FIRST)

### Why Core First?

From the grading criteria:

> **"Deliver a fully working, end-to-end system. For criteria that overlap with the mid-course test, you must meet all subcriteria to receive full points."**

This means:
- No Kafka → Cannot demo real-time data query → Lose 10+ pts
- No Airflow → Cannot demo dbt via orchestrator → Lose 7.5 pts
- No RAG → Cannot demo document query → Lose 10 pts

**Total risk: 27.5 core points**

---

### 1.1 Kafka Setup (Priority: CRITICAL)

**Time Estimate:** 30-45 minutes
**Points at Risk:** 7.5 core + 5 extra = 12.5 pts
**Complexity:** LOW (course provides templates)

**Why First:**
1. Required for `#live-demo` of real-time data
2. Agent needs Kafka tool to query streaming data
3. Course provides docker-compose template

**Architecture (from course):**
```
Producer (fake alerts) → Kafka Topic → Consumer → PostgreSQL (local)
                                                        ↓
                                                 Agent queries here
```

**Key insight:** Streaming pipeline is SEPARATE from batch (Snowflake). Uses local PostgreSQL as sink.

**What to Build:**

```
kafka/
├── docker-compose.yml      # Kafka + PostgreSQL containers
├── producer.py             # Generates fake alerts
├── consumer.py             # Writes alerts to PostgreSQL
├── test_setup.py           # Verify connections
└── .env                    # Config
```

**Data: Real-time Alerts (unrelated to batch analytics)**

| Field | Type | Example |
|-------|------|---------|
| `id` | UUID | auto-generated |
| `timestamp` | datetime | 2026-01-24T10:30:00 |
| `alert_type` | string | SPEND_SPIKE, ROAS_DROP, INSTALL_SURGE, ERROR_RATE |
| `severity` | string | info, warning, critical |
| `message` | string | "Unusual spend pattern in TH region" |
| `value` | float | 1250.00 |
| `created_at` | datetime | auto |

**Why alerts (not app metrics):**
- Different from batch data (no duplication of Snowflake data)
- Simple to generate with random values
- Makes business sense ("Show me recent alerts")
- Easy to demo

**Implementation:**

```yaml
# kafka/docker-compose.yml
version: '3.8'
services:
  kafka:
    image: confluentinc/cp-kafka:7.5.0
    hostname: kafka
    container_name: capstone-kafka
    ports:
      - "9092:9092"
      - "29092:29092"
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: 'CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT'
      KAFKA_ADVERTISED_LISTENERS: 'PLAINTEXT://kafka:9092,PLAINTEXT_HOST://localhost:29092'
      KAFKA_PROCESS_ROLES: 'broker,controller'
      KAFKA_CONTROLLER_QUORUM_VOTERS: '1@kafka:9093'
      KAFKA_LISTENERS: 'PLAINTEXT://kafka:9092,CONTROLLER://kafka:9093,PLAINTEXT_HOST://0.0.0.0:29092'
      KAFKA_CONTROLLER_LISTENER_NAMES: 'CONTROLLER'
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      CLUSTER_ID: 'MkU3OEVBNTcwNTJENDM2Qk'
    healthcheck:
      test: kafka-topics --bootstrap-server kafka:9092 --list
      interval: 30s
      timeout: 10s
      retries: 5

  postgres:
    image: postgres:15
    container_name: capstone-postgres
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: capstone
      POSTGRES_PASSWORD: capstone123
      POSTGRES_DB: streaming
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: pg_isready -U capstone -d streaming
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

```python
# kafka/producer.py
"""Fake alerts producer for demo - UNRELATED to batch data."""
import json
import time
import random
import uuid
from datetime import datetime
from kafka import KafkaProducer

ALERT_TYPES = ["SPEND_SPIKE", "ROAS_DROP", "INSTALL_SURGE", "ERROR_RATE"]
SEVERITIES = ["info", "warning", "critical"]
MESSAGES = {
    "SPEND_SPIKE": "Unusual spend pattern detected in {} region",
    "ROAS_DROP": "ROAS dropped below threshold for {}",
    "INSTALL_SURGE": "Install volume spike in {}",
    "ERROR_RATE": "Error rate increased for {} platform",
}
REGIONS = ["US", "TH", "VN", "JP", "ID"]

def generate_alert():
    alert_type = random.choice(ALERT_TYPES)
    region = random.choice(REGIONS)
    return {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "alert_type": alert_type,
        "severity": random.choice(SEVERITIES),
        "message": MESSAGES[alert_type].format(region),
        "value": round(random.uniform(100, 5000), 2),
    }

def main():
    producer = KafkaProducer(
        bootstrap_servers='localhost:29092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    print("Starting alert producer...")
    while True:
        alert = generate_alert()
        producer.send('alerts', alert)
        print(f"Sent: {alert['severity'].upper()} - {alert['message']}")
        time.sleep(10)  # Every 10 seconds

if __name__ == "__main__":
    main()
```

```python
# kafka/consumer.py
"""Alert consumer - writes to PostgreSQL."""
import json
import psycopg2
from kafka import KafkaConsumer

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="streaming",
        user="capstone",
        password="capstone123"
    )

def create_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id UUID PRIMARY KEY,
                timestamp TIMESTAMP,
                alert_type VARCHAR(50),
                severity VARCHAR(20),
                message TEXT,
                value DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()

def main():
    conn = get_db_connection()
    create_table(conn)

    consumer = KafkaConsumer(
        'alerts',
        bootstrap_servers='localhost:29092',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='earliest',
        group_id='alert-consumer'
    )

    print("Consuming alerts...")
    for message in consumer:
        alert = message.value
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO alerts (id, timestamp, alert_type, severity, message, value)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (alert['id'], alert['timestamp'], alert['alert_type'],
                  alert['severity'], alert['message'], alert['value']))
            conn.commit()
        print(f"Stored: {alert['severity']} - {alert['message']}")

if __name__ == "__main__":
    main()
```

**Demo Script:**
```bash
# Terminal 1: Start Kafka + PostgreSQL
cd kafka && docker-compose up -d

# Wait for healthy (check status)
docker-compose ps

# Terminal 2: Start consumer (writes to PostgreSQL)
uv run python kafka/consumer.py

# Terminal 3: Start producer (generates alerts)
uv run python kafka/producer.py

# Verify in PostgreSQL
docker exec -it capstone-postgres psql -U capstone -d streaming -c "SELECT * FROM alerts ORDER BY created_at DESC LIMIT 5;"
```

**Acceptance Criteria:**
- [ ] Kafka + PostgreSQL start without errors
- [ ] Producer sends alerts every 10 seconds
- [ ] Consumer writes alerts to PostgreSQL
- [ ] Agent can query alerts from PostgreSQL

---

### 1.2 Airflow Setup (Priority: CRITICAL)

**Time Estimate:** 30-45 minutes
**Points at Risk:** 7.5 core pts
**Complexity:** MEDIUM (Docker networking can be tricky)

**Why Second:**
1. Required for `#live-demo` of dbt via orchestrator
2. Must have 3+ tasks
3. Course provides templates

**What to Build:**

```
airflow/
├── docker-compose.yml      # Airflow + Redis
├── Dockerfile              # Custom image with dbt
├── dags/
│   └── dbt_pipeline.py     # Main DAG with 3 tasks
├── .env                    # Airflow config
└── requirements.txt        # dbt-snowflake
```

**DAG Implementation (from course):**

```python
# airflow/dags/dbt_pipeline.py
"""
dbt Pipeline DAG - 3 tasks for grading requirement
"""
import os
import pendulum
from airflow.decorators import dag, task
from datetime import timedelta

def get_dbt_env_vars():
    return {
        "SNOWFLAKE_ACCOUNT": "{{ conn.snowflake_default.extra_dejson.account }}",
        "SNOWFLAKE_USER": "{{ conn.snowflake_default.login }}",
        "SNOWFLAKE_PRIVATE_KEY_FILE_PWD": "{{ conn.snowflake_default.password }}",
        "SNOWFLAKE_ROLE": "{{ conn.snowflake_default.extra_dejson.role }}",
        "SNOWFLAKE_WAREHOUSE": "{{ conn.snowflake_default.extra_dejson.warehouse }}",
        "SNOWFLAKE_DATABASE": "{{ conn.snowflake_default.extra_dejson.database }}",
        "DBT_PROFILES_DIR": "/opt/airflow/.dbt",
        "DBT_PROJECT_DIR": "/opt/airflow/dbt_project",
    }

@dag(
    dag_id="capstone_dbt_pipeline",
    schedule="0 2 * * *",  # Daily at 2 AM
    start_date=pendulum.datetime(2025, 1, 1, tz="Asia/Bangkok"),
    catchup=False,
    tags=["capstone", "dbt"],
    max_active_runs=1,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    }
)
def capstone_dbt_pipeline():

    @task.bash(env={**get_dbt_env_vars()})
    def dbt_deps() -> str:
        """Task 1: Install dbt dependencies"""
        return "cd $DBT_PROJECT_DIR && dbt deps"

    @task.bash(env={**get_dbt_env_vars()})
    def dbt_run() -> str:
        """Task 2: Run dbt models"""
        return "cd $DBT_PROJECT_DIR && dbt run"

    @task.bash(env={**get_dbt_env_vars()})
    def dbt_test() -> str:
        """Task 3: Run dbt tests"""
        return "cd $DBT_PROJECT_DIR && dbt test"

    # Set dependencies: deps → run → test
    dbt_deps() >> dbt_run() >> dbt_test()

# Create DAG instance
capstone_dbt_pipeline()
```

**Demo Script:**
```bash
# Start Airflow
cd airflow && docker-compose up -d

# Wait for healthy (2-3 min)
docker-compose ps

# Open UI: http://localhost:8080 (airflow/airflow)
# Trigger DAG manually
# Show 3 tasks executing
```

**Acceptance Criteria:**
- [ ] Airflow UI accessible at localhost:8080
- [ ] DAG appears with 3 tasks
- [ ] DAG runs successfully
- [ ] dbt models build in Snowflake

---

### 1.3 Basic RAG (Priority: CRITICAL)

**Time Estimate:** 45-60 minutes
**Points at Risk:** 10 core pts
**Complexity:** MEDIUM

**Why Third:**
1. Required for `#live-demo` of document query
2. Agent needs RAG tool
3. Course uses Pinecone, but we can use FAISS (simpler, local)

**Decision: FAISS vs Pinecone**

| Factor | Pinecone | FAISS |
|--------|----------|-------|
| Setup | Need API key | Local, no API |
| Cost | Free tier limited | Free |
| Course alignment | Yes | Acceptable alternative |
| Simplicity | External dependency | Self-contained |

**Recommendation:** Use **FAISS** for simplicity. Course says alternatives are allowed.

**What to Build:**

```
agent/tools/
├── rag_tools.py           # RAG tool with FAISS
docs/
├── Business_Rules.pdf      # Sample doc for demo
└── vector_store/           # FAISS index storage
```

**Implementation:**

```python
# agent/tools/rag_tools.py
"""RAG tool using FAISS for document search."""
import os
from pathlib import Path
from typing import Annotated

from langchain_core.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Global vector store (initialized once)
_vector_store = None

def get_vector_store():
    """Get or create the FAISS vector store."""
    global _vector_store

    if _vector_store is not None:
        return _vector_store

    store_path = Path(__file__).parent.parent.parent / "docs" / "vector_store"

    # Try to load existing store
    if store_path.exists():
        embeddings = OpenAIEmbeddings()
        _vector_store = FAISS.load_local(
            str(store_path),
            embeddings,
            allow_dangerous_deserialization=True
        )
        return _vector_store

    # Create new store from PDFs
    docs_path = Path(__file__).parent.parent.parent / "docs"
    pdf_files = list(docs_path.glob("*.pdf"))

    if not pdf_files:
        return None

    # Load and split documents
    all_docs = []
    for pdf_file in pdf_files:
        loader = PyPDFLoader(str(pdf_file))
        docs = loader.load()
        all_docs.extend(docs)

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(all_docs)

    # Create vector store
    embeddings = OpenAIEmbeddings()
    _vector_store = FAISS.from_documents(chunks, embeddings)

    # Save for future use
    store_path.mkdir(parents=True, exist_ok=True)
    _vector_store.save_local(str(store_path))

    return _vector_store

@tool
def search_documents(
    query: Annotated[str, "Question to search in business documents"]
) -> str:
    """
    Search business documents for information about policies, guidelines, and rules.

    Use this tool when asked about:
    - Business rules and thresholds
    - Company policies
    - Metric definitions
    - Guidelines for decisions

    Args:
        query: The question to search for

    Returns:
        Relevant document excerpts
    """
    store = get_vector_store()

    if store is None:
        return "No documents available. Please add PDF files to the docs/ folder."

    # Search for relevant documents
    results = store.similarity_search(query, k=3)

    if not results:
        return f"No relevant documents found for: {query}"

    # Format results
    output = f"Found {len(results)} relevant excerpts:\n\n"
    for i, doc in enumerate(results, 1):
        source = doc.metadata.get('source', 'Unknown')
        output += f"**Source {i}:** {Path(source).name}\n"
        output += f"{doc.page_content}\n\n"

    return output
```

**Sample Document (create this):**

```
# docs/Business_Rules.pdf (content)

## Ameno Technologies - Business Rules

### ROAS Thresholds
- D0 ROAS > 100%: Profitable, can scale
- D0 ROAS 80-100%: Marginal, monitor D7
- D0 ROAS < 80%: Losing money, needs action

### CPI Guidelines
- CPI increase > 30%: Check creative fatigue
- CPI decrease > 20%: Good, consider scaling

### Decision Framework
- SCALE: ROAS > 120% for 3+ days
- MAINTAIN: ROAS 90-120%
- CUT: ROAS < 70% for 3+ days
```

**Acceptance Criteria:**
- [ ] PDF loads and chunks correctly
- [ ] Vector store creates/loads
- [ ] Search returns relevant results
- [ ] Agent can call the tool

---

### 1.4 Kafka Agent Tool (Priority: HIGH)

**Time Estimate:** 15 minutes
**Points at Risk:** 5 extra pts
**Complexity:** LOW

**Why After Kafka Setup:**
1. Depends on PostgreSQL being populated by consumer
2. Shows agent can query real-time data
3. Quick implementation

**Implementation:**

```python
# agent/tools/kafka_tools.py
"""Streaming alerts tool - queries PostgreSQL sink."""
import psycopg2
from typing import Annotated
from langchain_core.tools import tool

def get_db_connection():
    """Connect to streaming PostgreSQL database."""
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="streaming",
        user="capstone",
        password="capstone123"
    )

@tool
def query_realtime_alerts(
    severity: Annotated[str, "Filter by severity: 'all', 'critical', 'warning', or 'info'"] = "all",
    limit: Annotated[int, "Number of alerts to return"] = 10
) -> str:
    """
    Query real-time alerts from the streaming pipeline.

    Use this tool when asked about:
    - Recent alerts or notifications
    - Real-time monitoring events
    - Critical/warning alerts
    - Streaming data status

    The streaming pipeline is SEPARATE from batch analytics.
    It shows alerts like SPEND_SPIKE, ROAS_DROP, INSTALL_SURGE, ERROR_RATE.

    Args:
        severity: Filter by alert severity ('all', 'critical', 'warning', 'info')
        limit: Maximum number of alerts to return

    Returns:
        Recent alerts from the streaming pipeline
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        if severity == "all":
            cur.execute("""
                SELECT timestamp, alert_type, severity, message, value
                FROM alerts
                ORDER BY created_at DESC
                LIMIT %s
            """, (limit,))
        else:
            cur.execute("""
                SELECT timestamp, alert_type, severity, message, value
                FROM alerts
                WHERE severity = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (severity, limit))

        rows = cur.fetchall()
        cur.close()
        conn.close()

        if not rows:
            return f"No {severity} alerts found. The streaming pipeline may not be running."

        output = f"**Real-time Alerts** (last {len(rows)}):\n\n"
        for row in rows:
            ts, alert_type, sev, msg, val = row
            icon = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(sev, "⚪")
            output += f"{icon} **{sev.upper()}** [{alert_type}]\n"
            output += f"   {msg} (value: {val})\n"
            output += f"   _{ts}_\n\n"

        return output

    except Exception as e:
        return f"Error querying alerts: {str(e)}. Is the streaming pipeline running?"
```

**Acceptance Criteria:**
- [ ] Tool connects to PostgreSQL
- [ ] Returns recent alerts with severity filter
- [ ] Agent can call the tool and display results

---

## Phase 2: Quick Wins (SHOULD DO)

### 2.1 dbt Macros (Priority: MEDIUM)

**Time Estimate:** 30 minutes
**Points:** 10-15 extra pts
**Complexity:** LOW

**Why This:**
1. Already have 1 macro (calculate_ctr)
2. Easy to add more
3. Shows best practices
4. Directly addresses grading: "Custom dbt macros for complex transformations"

**What to Add:**

```sql
-- my_dbt_project/macros/calculate_roas.sql
{% macro calculate_roas(revenue_col, cost_col, multiplier=100) %}
{#
    Calculate ROAS (Return on Ad Spend).
    Usage: {{ calculate_roas('ad_revenue_d0', 'network_cost') }}
#}
CASE
    WHEN {{ cost_col }} > 0
    THEN ({{ revenue_col }}::DECIMAL / {{ cost_col }}) * {{ multiplier }}
    ELSE NULL
END
{% endmacro %}


-- my_dbt_project/macros/calculate_cpi.sql
{% macro calculate_cpi(cost_col, installs_col) %}
{#
    Calculate CPI (Cost Per Install).
    Usage: {{ calculate_cpi('network_cost', 'installs') }}
#}
CASE
    WHEN {{ installs_col }} > 0
    THEN {{ cost_col }}::DECIMAL / {{ installs_col }}
    ELSE NULL
END
{% endmacro %}


-- my_dbt_project/macros/calculate_ecpm.sql
{% macro calculate_ecpm(revenue_col, impressions_col) %}
{#
    Calculate eCPM (Revenue per 1000 impressions).
    Usage: {{ calculate_ecpm('ad_revenue', 'ad_impressions') }}
#}
CASE
    WHEN {{ impressions_col }} > 0
    THEN ({{ revenue_col }}::DECIMAL * 1000) / {{ impressions_col }}
    ELSE NULL
END
{% endmacro %}


-- my_dbt_project/macros/safe_divide.sql
{% macro safe_divide(numerator, denominator, default='NULL') %}
{#
    Null-safe division.
    Usage: {{ safe_divide('revenue', 'cost') }}
#}
CASE
    WHEN {{ denominator }} IS NOT NULL AND {{ denominator }} != 0
    THEN {{ numerator }}::DECIMAL / {{ denominator }}
    ELSE {{ default }}
END
{% endmacro %}
```

**Update Model to Use Macros:**

```sql
-- models/03_mart/fct_app_daily_performance.sql (add computed columns)
SELECT
    ...
    -- Computed metrics using macros
    {{ calculate_roas('m.ad_revenue_d0', 'm.network_cost') }} AS d0_roas_pct,
    {{ calculate_roas('m.ad_revenue_d7', 'm.network_cost') }} AS d7_roas_pct,
    {{ calculate_cpi('m.network_cost', 'm.installs') }} AS cpi_usd,
    {{ calculate_ecpm('m.ad_revenue', 'm.ad_impressions') }} AS ecpm_usd,
FROM metrics m
```

**Acceptance Criteria:**
- [ ] Macros compile without errors
- [ ] `dbt compile` shows macro expansion
- [ ] Computed columns appear in fact table

---

### 2.2 dbt-expectations (Priority: MEDIUM)

**Time Estimate:** 30 minutes
**Points:** 10-15 extra pts
**Complexity:** LOW

**Why This:**
1. Directly addresses "Data quality validation with automated alerts"
2. Package is well-documented
3. Easy to add tests

**Implementation:**

```yaml
# my_dbt_project/packages.yml (update)
packages:
  - package: dbt-labs/dbt_utils
    version: 1.1.1
  - package: calogica/dbt_expectations
    version: 0.10.4
```

```yaml
# my_dbt_project/models/03_mart/schema.yml (enhanced)
version: 2

models:
  - name: fct_app_daily_performance
    description: "Fact table with data quality gates"

    # Table-level tests
    tests:
      # Freshness check
      - dbt_expectations.expect_row_values_to_have_recent_data:
          datepart: day
          interval: 3
          timestamp_column: dbt_updated_at
          severity: warn

    columns:
      - name: ad_revenue
        description: "AdMob revenue (source of truth)"
        data_tests:
          - not_null
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
              max_value: 100000
              severity: warn

      - name: network_cost
        data_tests:
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
              max_value: 50000

      - name: installs
        data_tests:
          - not_null
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
              max_value: 100000
```

**Commands:**
```bash
cd my_dbt_project
dbt deps  # Install packages
dbt test  # Run tests
```

**Acceptance Criteria:**
- [ ] Package installs successfully
- [ ] Tests pass (or warn appropriately)
- [ ] Can show test results in demo

---

### 2.3 Enhanced Prompts Documentation (Priority: MEDIUM)

**Time Estimate:** 20 minutes
**Points:** 5-10 extra pts
**Complexity:** LOW

**Why This:**
1. We ALREADY HAVE good prompts
2. Just need to document them better
3. Shows "Custom prompt engineering for better responses"

**What to Do:**

1. Update `agent/prompts.py` with more detailed comments
2. Add business context section
3. Document the thresholds and decision framework

This is already partially done - just needs polish and documentation.

---

## Phase 3: Nice to Have (IF TIME PERMITS)

### 3.1 Hybrid Search RAG

**Time Estimate:** 1-2 hours
**Points:** 15-20 extra pts
**Complexity:** HIGH

**Why Valuable:**
- Course explicitly mentions this as "advanced feature not included in lab"
- Shows innovation beyond course material
- 35% accuracy improvement (measurable)

**Only do if:**
- Core checkboxes are done
- Quick wins are done
- Have 2+ hours before demo

---

### 3.2 Multi-Model Orchestration

**Time Estimate:** 2-3 hours
**Points:** 15-20 extra pts
**Complexity:** HIGH

**Why Valuable:**
- Innovative (not in course)
- Shows production thinking
- Cost optimization story

**Only do if:**
- All above is done
- Want to push for 90+ pts

---

## Demo Day Checklist

### Morning Prep (1 hour before)

```bash
# 1. Collect fresh data
python scripts/collect_adjust_capstone.py --days 1
python scripts/collect_admob_capstone.py --days 1

# 2. Run dbt
cd my_dbt_project && dbt build

# 3. Start services
cd kafka && docker-compose up -d
cd airflow && docker-compose up -d

# 4. Start Kafka producer
uv run python kafka/producer.py &

# 5. Test agent
uv run python -m agent.agent --query "What's total revenue today?"
```

### Demo Flow (30 minutes)

| Time | What to Show | Script |
|------|--------------|--------|
| 0-5 | Real-time Pipeline | Start producer, show data flowing |
| 5-10 | Batch Pipeline | Trigger Airflow DAG, show dbt run |
| 10-20 | AI Agent | Query batch data, real-time, documents |
| 20-30 | Extra Features + Q&A | Show macros, tests, prompts |

### Talking Points

1. **Kafka**: "Real-time metrics with < 5 min latency"
2. **Airflow**: "Orchestrated dbt with 3 tasks: deps, run, test"
3. **RAG**: "Document search for business rules"
4. **Agent**: "Unified interface for Chi Linh"
5. **Extras**: "Custom macros, data quality tests, business context prompts"

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Kafka won't start | HIGH | Have backup data, skip streaming demo |
| Airflow complex | MEDIUM | Use course docker-compose as-is |
| RAG fails | MEDIUM | FAISS is simpler than Pinecone |
| Time runs out | HIGH | Do core checkboxes FIRST |

---

## Final Recommendation

### If You Have 4 Hours:

1. Kafka (45 min)
2. Airflow (45 min)
3. Basic RAG (60 min)
4. Kafka Tool (15 min)
5. dbt Macros (30 min)
6. dbt-expectations (30 min)
7. Test & Polish (30 min)

**Expected Score: 80-85 pts**

### If You Have 6+ Hours:

All above PLUS:
- Hybrid RAG (1.5 hrs)
- Multi-model routing (2 hrs)

**Expected Score: 90-95 pts**

### If You Only Have 2 Hours:

1. Kafka (45 min)
2. Airflow (45 min)
3. Basic RAG (30 min - simplified)

**Expected Score: 70-75 pts** (still passes!)

---

## Start Here

```bash
# Step 1: Create Kafka directory
mkdir -p kafka
cd kafka

# Step 2: Copy this docker-compose.yml (from course template)
# Step 3: Create producer.py
# Step 4: Test it works

# Then move to Airflow, then RAG, etc.
```

**Time starts now. Good luck!**
