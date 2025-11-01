# Mid-Course Test - Quick Guide

## Setup (One-Time)

```bash
uv run python scripts/setup/create_raw_midtest_schema.py
```

## Data Collection

**Batch Mode** (same loaded_at):
```bash
uv run python scripts/collect_admob_midtest.py --batch
uv run python scripts/collect_adjust_midtest.py --batch
```

**Realtime Mode** (staggered loaded_at, multithreaded):
```bash
uv run python scripts/collect_admob_midtest.py --realtime
uv run python scripts/collect_adjust_midtest.py --realtime
```

## Validation

Run queries in `VALIDATE_MIDTEST.sql` in Snowflake to verify:

1. ✅ Tables exist (ADMOB_DAILY_MIDTEST, ADJUST_DAILY_MIDTEST)
2. ✅ 3 apps in each table
3. ✅ Batch mode: all rows same LOADED_AT
4. ✅ Realtime mode: each row different LOADED_AT
5. ✅ All rows have unique RAW_RECORD_ID (UUID for data lineage)

## What You Get

- **Schema**: RAW_MIDTEST
- **Apps**: 3 apps only (video.ai.videogenerator, ai.video.generator.text.video, text.to.video.aivideo.generator)
- **Data**: Last 7 days, altered ±50% for demo
- **Lineage**: RAW_RECORD_ID (UUID), BATCH_ID, LOADED_AT

---

**Next**: dbt transformation layers
