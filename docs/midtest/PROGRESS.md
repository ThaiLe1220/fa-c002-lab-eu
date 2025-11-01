# Mid-Course Test Progress

## ✅ Completed

### 1. Data Ingestion Setup
- Created RAW_MIDTEST schema in Snowflake
- Created ADMOB_DAILY_MIDTEST and ADJUST_DAILY_MIDTEST tables
- Added data lineage tracking (RAW_RECORD_ID UUID, BATCH_ID, LOADED_AT)

### 2. Collection Scripts
- `scripts/setup/create_raw_midtest_schema.py` - one-time schema setup
- `scripts/collect_admob_midtest.py` - AdMob data collection (batch/realtime modes)
- `scripts/collect_adjust_midtest.py` - Adjust data collection (batch/realtime modes)

### 3. Key Features
- **3 apps only**: video.ai.videogenerator, ai.video.generator.text.video, text.to.video.aivideo.generator
- **Batch mode**: All rows same LOADED_AT timestamp
- **Realtime mode**: 10-20 rows, multithreaded, staggered LOADED_AT
- **Data alterations**: ±50% random changes for repeatability
- **Last 7 days**: Consistent date range

### 4. Documentation
- MIDTEST_QUICK_GUIDE.md - setup and usage guide
- PROGRESS.md - this file

## 📋 Next Steps

### Phase 1: dbt Staging Layer
**Goal**: Clean and standardize raw data

Files to create:
- `models/staging/midtest/stg_admob_midtest.sql`
- `models/staging/midtest/stg_adjust_midtest.sql`
- `models/staging/midtest/schema.yml` (tests)

Tasks:
- Clean column names (lowercase, standardize)
- Type casting and validation
- Add source freshness checks
- Basic data quality tests (not_null, unique)

**Estimated time**: 15 min

### Phase 2: dbt Intermediate Layer
**Goal**: Business logic and transformations

Files to create:
- `models/intermediate/midtest/int_app_daily_metrics.sql`
- `models/intermediate/midtest/schema.yml`

Tasks:
- Join AdMob + Adjust by app_store_id/store_id + date
- Calculate combined metrics (total revenue, ROAS, retention)
- Incremental materialization
- Relationship tests

**Estimated time**: 20 min

### Phase 3: dbt Mart Layer (Star Schema)
**Goal**: Analytics-ready dimensional model

Files to create:
- `models/marts/midtest/fct_app_daily_performance.sql` (fact table)
- `models/marts/midtest/dim_apps.sql` (dimension)
- `models/marts/midtest/dim_dates.sql` (dimension)
- `models/marts/midtest/dim_countries.sql` (dimension)
- `models/marts/midtest/schema.yml`

Tasks:
- Star schema implementation
- Surrogate keys for dimensions
- Comprehensive tests
- Generate ERD

**Estimated time**: 20 min

### Phase 4: Testing & Documentation
**Goal**: Quality assurance and documentation

Tasks:
- Custom macros for data quality
- dbt docs generate
- ERD diagram
- README for demo

**Estimated time**: 10 min

## 🎯 Demo Points Coverage

### Data Ingestion (35 pts)
- ✅ Git workflow (feature branches)
- ✅ Python data collection pipelines
- ✅ Data lineage tracking (UUID)
- ✅ Batch vs realtime patterns
- ⏳ Docker PostgreSQL (if needed)

### Transformation (40 pts)
- ⏳ Multi-layer dbt models (staging → intermediate → mart)
- ⏳ Incremental materialization
- ⏳ Custom macros
- ⏳ ERD diagram
- ⏳ Schema tests

### CI/CD (5 pts)
- ⏳ GitHub Actions
- ⏳ Automated checks

### Extra Features (20 pts)
- ⏳ Advanced transformations
- ⏳ Complex business logic
- ⏳ Additional data quality measures

**Current estimate**: ~20/100 points
**Target**: 70+ points (50+ to pass)

## 🔧 Technical Stack

- **Python**: 3.12 with uv package manager
- **Snowflake**: DB_T34.RAW_MIDTEST
- **dbt**: Not yet implemented
- **Git**: Feature branches, clean commits
- **APIs**: AdMob, Adjust

## 📝 Notes

- Data altered ±50% so can run multiple times for demo
- 3 apps only keeps scope manageable
- RAW_MIDTEST schema isolates test data
- All scripts use `uv run python` for consistency
