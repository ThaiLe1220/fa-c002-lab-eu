# Data Modeling Approach: Dimensional Modeling (Star Schema)

## Methodology

**Chosen Approach**: Dimensional Modeling with Star Schema pattern

**Rationale**:
- Optimized for analytical queries and business intelligence
- Simple structure easy for business users to understand
- Efficient query performance on Snowflake columnar storage
- Supports flexible aggregation and drill-down analysis

## Star Schema Design

### Fact Table: `fct_app_daily_performance`
**Grain**: One row per app per day per country

**Metrics**:
- Ad revenue, impressions, clicks, CTR (AdMob)
- Installs, sessions, DAUs (Adjust)
- Calculated: revenue per install, revenue per session

**Foreign Keys**:
- `app_key` → dim_apps
- `date_key` → dim_dates
- `country_code` (degenerate dimension)

### Dimension Tables

**`dim_apps`**:
- `app_key` (PK - surrogate key using MD5)
- `app_store_id` (natural key)
- `app_name` (friendly display name)

**`dim_dates`**:
- `date_key` (PK - surrogate key using MD5)
- `date` (natural key)
- Year, month, day, day_of_week, day_name

## Entity Relationship Diagram

```
┌─────────────────────────┐
│      dim_apps           │
├─────────────────────────┤
│ PK: app_key             │
│     app_store_id        │
│     app_name            │
└──────────┬──────────────┘
           │
           │ 1
           │
           │
           │ N
┌──────────▼──────────────────────────┐
│   fct_app_daily_performance         │
├─────────────────────────────────────┤
│ PK: performance_key                 │
│ FK: app_key                         │
│ FK: date_key                        │
│     country_code                    │
│     platform                        │
├─────────────────────────────────────┤
│ MEASURES:                           │
│   ad_revenue                        │
│   ad_impressions                    │
│   ad_clicks                         │
│   ad_ctr                            │
│   installs                          │
│   sessions                          │
│   daus                              │
│   revenue_per_install               │
│   revenue_per_session               │
└──────────┬──────────────────────────┘
           │
           │ N
           │
           │
           │ 1
┌──────────▼──────────────┐
│      dim_dates          │
├─────────────────────────┤
│ PK: date_key            │
│     date                │
│     year                │
│     month               │
│     day                 │
│     day_of_week         │
│     day_name            │
└─────────────────────────┘
```

## Relationships

- **dim_apps** → **fct_app_daily_performance**: 1:N (one app has many daily records)
- **dim_dates** → **fct_app_daily_performance**: 1:N (one date has many app/country records)

## Key Design Decisions

1. **Surrogate Keys**: MD5 hash for dimension keys (stable, consistent)
2. **Degenerate Dimensions**: country_code, platform stored in fact table (low cardinality)
3. **Star Schema vs Snowflake**: Chose star for simplicity and query performance
4. **Grain Selection**: Daily grain balances detail with query performance
5. **Incremental Processing**: Intermediate layer uses incremental materialization for efficiency

## dbt Implementation Layers

1. **Staging** (`01_staging`): Clean and standardize raw data
2. **Intermediate** (`02_intermediate`): Join AdMob + Adjust, calculate metrics (incremental)
3. **Mart** (`03_mart`): Star schema with fact + dimension tables (final analytics layer)

## Business Questions Supported

- Revenue analysis by app, date, country
- Customer acquisition metrics (installs, DAUs)
- Ad performance (CTR, revenue per session)
- Time-series trends and seasonality
- Geographic performance comparison
- ROI and efficiency metrics
