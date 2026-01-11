# FA-C002 Lab

This is the execution repo for the FA-C002 capstone project. It contains dbt models, data collection scripts, and CI/CD workflows for a mobile analytics data pipeline.

The pipeline combines AdMob (ad revenue) and Adjust (user acquisition metrics) data into a star schema in Snowflake. Data volume is around 4K rows daily for each source across all apps.

## Schema

Raw data lands in `DB_T34.RAW_CAPSTONE` with two tables: `ADJUST_DAILY` and `ADMOB_DAILY`. The dbt models transform this into a star schema in `DB_T34.ANALYTICS`.

## Quick Commands

```bash
cd my_dbt_project && source ../.venv/bin/activate && dbt build
```

For full command reference, see `docs/quick_start.md`.

## Key Files

The dbt models live in `my_dbt_project/models/` with three layers:

- **Staging** (`01_staging/`): `stg_adjust_midtest.sql` and `stg_admob_midtest.sql` clean raw data. These will be renamed to remove the "midtest" suffix.
- **Intermediate** (`02_intermediate/`): `int_app_daily_metrics.sql` joins both sources with a FULL OUTER JOIN and calculates derived metrics.
- **Mart** (`03_mart/`): `fct_app_daily_performance.sql` is the fact table, with `dim_apps.sql` and `dim_dates.sql` as dimensions.

Collection scripts are in `scripts/` - `collect_adjust_capstone.py` and `collect_admob_capstone.py` fetch from APIs and load to Snowflake.

## Business Context

D0 (Day 0) metrics are critical for this business. Around 70-80% of ad revenue comes from the install day, so tracking D0 revenue and impressions is essential for ROAS (Return on Ad Spend) analysis.

Key metrics: `ad_revenue_d0`, `ad_impressions_d0`, `network_cost`, `paid_impressions`, `subscrevnt_revenue`. Target ROAS > 1.0.

For full business logic and metric formulas, see `docs/planning/data_strategy.md` or `fa-c002-capstone/docs/DATA_SCHEMA.md`.

## Workflow

When working here: move fast, write working code, run tests (`dbt test`), and update docs when making changes.

## Reference

Canonical documentation lives in the capstone repo at `fa-c002-capstone/docs/`:

- `CAPSTONE_MVP_PLAN.md` for project phases and timeline
- `DATA_SCHEMA.md` for schema and metrics
- `API_CAPABILITIES.md` for API limits and available dimensions
- `DBT_D0_UPDATE_PLAN.md` for the D0 columns implementation plan

Communication style: direct, show code, skip lengthy explanations unless asked.
