# API Validation Scripts

✅ **Validation complete** - See `docs/planning/api_validation_results.md` for full results

## Scripts

- `test_api_capabilities.py` - AdMob API dimension/metric validation
- `test_hour_dimension.py` - AdMob HOUR dimension investigation (confirmed NOT available)
- `test_adjust_capabilities.py` - Adjust API endpoint validation (confirmed hourly data available)

## Usage

```bash
# Run individual tests
python scripts/validation/test _api_capabilities.py
python scripts/validation/test_hour_dimension.py
python scripts/validation/test_adjust_capabilities.py
```

## Key Findings

**AdMob:**
- Daily granularity only (HOUR not available)
- 13,508 rows/day
- All target dimensions work

**Adjust:**
- Hourly granularity available
- 936 rows/day (hourly)
- Cohort retention available

See full results: `docs/planning/api_validation_results.md`
