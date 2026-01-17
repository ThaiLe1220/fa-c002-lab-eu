# Architecture

## System Overview

**Three Independent Systems → One Agent**

```
┌─────────────────────────────────────────────────────────────────┐
│                         AI AGENT                                │
│              LangGraph + Memory + Business Context              │
│                                                                 │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐          │
│  │ Snowflake   │   │   Kafka     │   │    RAG      │          │
│  │   Tool      │   │   Tool      │   │   Tool      │          │
│  └─────────────┘   └─────────────┘   └─────────────┘          │
└─────────────────────────────────────────────────────────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   SYSTEM 1    │   │   SYSTEM 2    │   │   SYSTEM 3    │
│  Batch Data   │   │  Streaming    │   │  Documents    │
├───────────────┤   ├───────────────┤   ├───────────────┤
│ Real AdMob/   │   │ Fake metrics  │   │ Any PDF       │
│ Adjust data   │   │ Local Kafka   │   │ Vector store  │
│ Snowflake     │   │ Docker        │   │ Chroma/FAISS  │
│ dbt transform │   │               │   │               │
│               │   │               │   │               │
│ CORE VALUE    │   │ CHECKBOX      │   │ CHECKBOX      │
└───────────────┘   └───────────────┘   └───────────────┘
```

**Key Point:** Systems 2 and 3 are independent. They don't integrate with System 1. The agent queries each separately.

---

## System 1: Batch Data Pipeline (Core)

### Data Flow

```
PYTHON COLLECTION           SNOWFLAKE RAW              DBT TRANSFORMATION         ANALYTICS
┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
│ collect_admob   │───────▶│ ADMOB_DAILY     │───────▶│ stg_admob       │───┐    │ dim_apps        │
│ collect_adjust  │───────▶│ ADJUST_DAILY    │───────▶│ stg_adjust      │───┼───▶│ dim_dates       │
└─────────────────┘        └─────────────────┘        └─────────────────┘   │    │ fct_performance │
                                                              │             │    └─────────────────┘
                                                              ▼             │
                                                      ┌─────────────────┐   │
                                                      │ int_app_daily   │───┘
                                                      │ _metrics        │
                                                      └─────────────────┘
```

**Schema:** `DB_T34.RAW_CAPSTONE` (raw) → `DB_T34.ANALYTICS` (mart)

### Star Schema

```
                    ┌─────────────────────────────────────────┐
                    │         fct_app_daily_performance       │
                    ├─────────────────────────────────────────┤
                    │ performance_key (PK)                    │
┌──────────────┐    │ app_key (FK) ─────────────────────────┐ │    ┌──────────────┐
│   dim_apps   │    │ date_key (FK) ───────────────────────┐│ │    │  dim_dates   │
├──────────────┤    │ country_code                         ││ │    ├──────────────┤
│ app_key (PK) │◀───│ platform                             ││ │───▶│ date_key (PK)│
│ app_store_id │    │                                      ││ │    │ date         │
│ app_name     │    │ -- Raw Metrics --                    ││ │    │ year         │
└──────────────┘    │ ad_revenue                           ││ │    │ month        │
                    │ ad_impressions                       ││ │    │ day          │
                    │ ad_clicks                            ││ │    │ day_of_week  │
                    │ installs                             ││ │    │ day_name     │
                    │ clicks                               ││ │    └──────────────┘
                    │ daus                                 ││ │
                    │ network_cost                         ││ │
                    │ ad_revenue_d0                        ││ │
                    │ ad_impressions_d0                    ││ │
                    │ paid_impressions                     ││ │
                    │ subscrevnt_revenue                   ││ │
                    │                                      ││ │
                    │ -- Calculated --                     ││ │
                    │ ad_ctr                               ││ │
                    │ d0_revenue_pct                       │└─┘
                    │ dbt_updated_at                       │
                    └─────────────────────────────────────────┘
```

**Grain:** One row per app × date × country × platform

### dbt Layers

| Layer | Model | Type | Purpose |
|-------|-------|------|---------|
| Staging | stg_admob_capstone | View | Clean AdMob data |
| Staging | stg_adjust_capstone | View | Clean Adjust data |
| Intermediate | int_app_daily_metrics | Incremental | Join sources |
| Mart | dim_apps | Table | App dimension |
| Mart | dim_dates | Table | Date dimension |
| Mart | fct_app_daily_performance | Table | Fact table |

### Metrics Strategy

**Stored in fact table (raw):**
- ad_revenue, ad_impressions, ad_clicks
- installs, clicks, daus
- network_cost, ad_revenue_d0, ad_impressions_d0
- paid_impressions, subscrevnt_revenue

**Calculated at query time (aggregate):**
```sql
d0_roas = SUM(ad_revenue_d0) / NULLIF(SUM(network_cost), 0)
cpi = SUM(network_cost) / NULLIF(SUM(installs), 0)
ecpm = SUM(ad_revenue) * 1000 / NULLIF(SUM(ad_impressions), 0)
```

See `DATA_STRATEGY.md` for complete metric formulas.

---

## System 2: Streaming (Checkbox)

### Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Fake Producer   │────▶│  Kafka Topic    │────▶│    Consumer     │
│ (Python)        │     │  (Docker)       │     │    (Python)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                │
                                ▼
                        ┌─────────────────┐
                        │  Agent Tool     │
                        │  (query latest) │
                        └─────────────────┘
```

### Purpose

- Demonstrate streaming capability
- Independent from batch pipeline
- Uses fabricated/simulated data

### Components

- `kafka/docker-compose.yml` - Kafka + Zookeeper
- `kafka/producer.py` - Generate fake metrics
- `kafka/consumer.py` - Read and store
- `agent/tools/kafka_tools.py` - Agent queries latest

---

## System 3: RAG Documents (Checkbox)

### Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   PDF Docs      │────▶│  Chunking +     │────▶│  Vector Store   │
│   (any docs)    │     │  Embedding      │     │  (Chroma/FAISS) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                                ┌─────────────────┐
                                                │  Agent Tool     │
                                                │  (RAG query)    │
                                                └─────────────────┘
```

### Purpose

- Demonstrate RAG capability
- Answer questions about documents
- Independent from data pipeline

### Components

- `agent/rag/document_loader.py` - Load and chunk PDFs
- `agent/rag/vector_store.py` - Embed and store
- `agent/tools/rag_tools.py` - Agent retrieval tool

---

## Raw Layer Schema

### ADMOB_DAILY (RAW_CAPSTONE)

```sql
CREATE TABLE RAW_CAPSTONE.ADMOB_DAILY (
    RAW_RECORD_ID VARCHAR PRIMARY KEY,
    BATCH_ID VARCHAR,
    DATE VARCHAR,
    APP_STORE_ID VARCHAR,
    APP_NAME VARCHAR,
    COUNTRY_CODE VARCHAR,
    PLATFORM VARCHAR,
    ESTIMATED_EARNINGS NUMBER,
    AD_IMPRESSIONS NUMBER,
    AD_CLICKS NUMBER,
    AD_REQUESTS NUMBER,
    MATCHED_REQUESTS NUMBER,
    OBSERVED_ECPM NUMBER,
    LOADED_AT TIMESTAMP
);
```

### ADJUST_DAILY (RAW_CAPSTONE)

```sql
CREATE TABLE RAW_CAPSTONE.ADJUST_DAILY (
    RAW_RECORD_ID VARCHAR PRIMARY KEY,
    BATCH_ID VARCHAR,
    DAY DATE,
    STORE_ID VARCHAR,
    APP VARCHAR,
    COUNTRY_CODE VARCHAR,
    OS_NAME VARCHAR,
    INSTALLS NUMBER,
    CLICKS NUMBER,
    DAUS NUMBER,
    AD_REVENUE NUMBER,
    AD_IMPRESSIONS NUMBER,
    AD_REVENUE_TOTAL_D0 NUMBER,
    AD_IMPRESSIONS_TOTAL_D0 NUMBER,
    NETWORK_COST NUMBER,
    PAID_IMPRESSIONS NUMBER,
    SUBSCREVNT_REVENUE NUMBER,
    LOADED_AT TIMESTAMP
);
```

---

## Data Volume

| Table | Daily Volume | Monthly |
|-------|--------------|---------|
| ADMOB_DAILY | ~1,500 rows | ~45K rows |
| ADJUST_DAILY | ~4,000 rows | ~120K rows |
| fct_app_daily_performance | ~4,000 rows | ~120K rows |

---

## Key Design Decisions

| Decision | Choice | Reasoning |
|----------|--------|-----------|
| Star schema | Yes | Industry standard, good for analytics |
| 3 dbt layers | Yes | Clear separation, debuggable |
| Incremental | Yes | Required by grading, efficient |
| Raw metrics in fact | Yes | Flexibility for different aggregations |
| 3 independent systems | Yes | Simpler implementation, meets requirements |
