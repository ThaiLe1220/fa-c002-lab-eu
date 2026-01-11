# FA-C002 Lab - Mobile Analytics Pipeline

**Execution repo** for FA-C002 capstone project. Contains dbt models, collection scripts, and CI/CD.

**Canonical documentation:** [`fa-c002-capstone/docs/`](../fa-c002-capstone/docs/)

## Data Sources

| Source | Schema | Volume | Key Metrics |
|--------|--------|--------|-------------|
| Adjust API | `RAW_CAPSTONE.ADJUST_DAILY` | ~4K rows/day | installs, daus, ad_revenue, network_cost, D0 metrics |
| AdMob API | `RAW_CAPSTONE.ADMOB_DAILY` | ~1.5K rows/day | estimated_earnings, impressions, eCPM |

## Quick Commands

```bash
# Activate environment
source .venv/bin/activate

# Data collection
python scripts/collect_adjust_capstone.py   # Adjust → RAW_CAPSTONE
python scripts/collect_admob_capstone.py    # AdMob → RAW_CAPSTONE

# dbt
cd my_dbt_project
dbt run --select staging
dbt run --select mart
dbt test
```

## Project Structure

```
fa-c002-lab/
├── CLAUDE.md                    # Agent instructions
├── scripts/
│   ├── collect_adjust_capstone.py
│   └── collect_admob_capstone.py
├── my_dbt_project/
│   └── models/
│       ├── 01_staging/          # stg_adjust, stg_admob
│       ├── 02_intermediate/     # int_app_daily_metrics
│       └── 03_mart/             # fct_app_daily_performance
└── docs/
    ├── planning/                # API validation, data strategy
    └── _archive/midterm/        # Archived midterm docs
```

## Tech Stack

- **dbt** - SQL transformations
- **Snowflake** - Data warehouse (`DB_T34.RAW_CAPSTONE`)
- **Python** - API collection scripts
- **GitHub Actions** - CI/CD

## Documentation

| Doc | Location |
|-----|----------|
| Full project plan | `fa-c002-capstone/docs/CAPSTONE_MVP_PLAN.md` |
| Data schema | `fa-c002-capstone/docs/DATA_SCHEMA.md` |
| API capabilities | `fa-c002-capstone/docs/API_CAPABILITIES.md` |
| Metrics formulas | `fa-c002-capstone/docs/BUSINESS_CONTEXT.md` |
| Setup guide | `docs/00_setup_guide.md` |
| Snowflake RSA setup | `docs/snowflake_setup.md` |

---

**Last Updated:** January 11, 2026
