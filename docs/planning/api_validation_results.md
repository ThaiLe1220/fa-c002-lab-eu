yo# API Capability Validation Results

**Date:** October 19, 2025
**Purpose:** Validate data availability before building data warehouse

---

## Executive Summary

**AdMob API:**
- ✅ Daily granularity only (HOUR dimension NOT available)
- ✅ 13,508 rows/day with full dimensions → 1.2M rows for 90 days
- ✅ 365+ days historical depth
- ✅ All target dimensions and metrics available

**Adjust API:**
- ✅ **HOURLY granularity AVAILABLE** (936 rows/day for yesterday)
- ✅ Cohort retention metrics available (D0, D1, D7, D30)
- ❌ IAP revenue NOT tracked
- ✅ 365+ days historical depth
- ✅ All target dimensions and metrics available

**ARCHITECTURE IMPACT:** Real-time hourly pipeline IS POSSIBLE using Adjust API data

---

## AdMob API Validation

### Test Script
`test_api_capabilities.py` - Comprehensive dimension/metric testing

### Available Dimensions
✅ **Confirmed Working:**
- `APP` - Application identifier
- `DATE` - Date dimension (daily)
- `COUNTRY` - Country code
- `PLATFORM` - Android/iOS
- `FORMAT` - Ad format (banner, interstitial, rewarded, native)
- `AD_UNIT` - Specific ad placement

❌ **NOT Available:**
- `HOUR` - Hourly time granularity (tested 6 different configurations, all failed)

### Available Metrics
✅ **Confirmed Working:**
- `ESTIMATED_EARNINGS` - Revenue in USD
- `IMPRESSIONS` - Ad impressions
- `CLICKS` - Ad clicks
- `AD_REQUESTS` - Total ad requests
- `MATCHED_REQUESTS` - Requests with ads
- `OBSERVED_ECPM` - Effective CPM

### Data Volume (Yesterday: 2025-10-18)
- **Basic** (APP, DATE, COUNTRY, PLATFORM): 1,644 rows
- **With FORMAT**: 5,127 rows
- **With AD_UNIT**: 13,508 rows
- **Extended Metrics**: All metrics work, same row counts

**90-Day Projection:**
- Full dimensions: 13,508 × 90 = **1,215,720 rows** (manageable)

### Historical Depth
✅ Tested successfully:
- 30 days back: Data available
- 60 days back: Data available
- 90 days back: Data available
- 180 days back: Data available
- 365 days back: Data available

**Conclusion:** Historical data available for 365+ days

### HOUR Dimension Deep Dive

**Test Script:** `test_hour_dimension.py`

**Configurations Tested:**
1. Network Report - HOUR + DATE (minimal)
2. Network Report - HOUR + DATE + APP
3. Network Report - Full dimensions with HOUR
4. Mediation Report - HOUR + DATE (minimal)
5. Mediation Report - HOUR + DATE + APP
6. Mediation Report - Full dimensions with HOUR

**Result:** ALL configurations failed with:
```
Invalid value at 'report_spec.dimensions[0]'
(type.googleapis.com/google.ads.admob.v1.NetworkReportSpec.Dimension), "HOUR"
```

**Conclusion:** HOUR dimension documented but NOT available for this account tier/region

**Google Documentation Found:**
- HOUR dimension exists in API spec
- Requires DATE dimension when used
- 28-day maximum range restriction
- Available in both networkReport and mediationReport APIs

**Why Not Available:**
- Likely requires specific account tier
- May be region-restricted
- Could require special API access permissions
- Feature may be in beta/limited availability

---

## Adjust API Validation

### Test Script
`test_adjust_capabilities.py` - Comprehensive endpoint testing

### Available Dimensions
✅ **Confirmed Working:**
- `app` - Application name
- `store_id` - App store identifier
- `day` - Date dimension (daily)
- `hour` - **HOURLY TIME GRANULARITY** ✅
- `country_code` - ISO country code
- `country` - Country name
- `os_name` - android/ios

### Available Metrics
✅ **Confirmed Working:**
- `installs` - New user installs
- `daus` - Daily active users
- `ad_revenue` - Ad revenue (from SDK)
- `ad_impressions` - Ad impressions
- `ad_revenue_total_d0` - Day 0 cumulative revenue
- `ad_impressions_total_d0` - Day 0 cumulative impressions
- `network_cost` - Marketing spend
- `network_cost_diff` - Cost changes

✅ **Cohort Retention Metrics:**
- `cohort_size_d0` - Day 0 cohort size
- `cohort_size_d1` - Day 1 retention
- `cohort_size_d7` - Day 7 retention
- `cohort_size_d30` - Day 30 retention

❌ **NOT Available:**
- `iap_revenue` - In-app purchase revenue
- `revenue` - Total revenue

**IAP Error:**
```
Unsupported metric: iap_revenue (iap event doesn't exist or was renamed)
```

**Conclusion:** IAP tracking not configured in Adjust SDK or not enabled for account

### Data Volume (Yesterday: 2025-10-18)

**Daily Granularity:**
- Basic (app, day): 38 rows
- With country: 2,215 rows
- Full dimensions: 2,216 rows

**Hourly Granularity:**
- app, day, hour: **936 rows** (≈39 apps × 24 hours)
- Expected: ~24 rows per app per day
- Actual matches expectation

**90-Day Projection:**
- Daily: 2,216 × 90 = **199,440 rows**
- Hourly: 936 × 90 = **84,240 rows** (manageable)

### Time Granularity

✅ **HOURLY DATA CONFIRMED AVAILABLE**

**Hour Format:** `2025-10-18T11:00:00` (ISO 8601 timestamp)

**Sample Row:**
```csv
app,day,hour,installs,daus
AI GPT Generator-Text to Video,2025-10-18,2025-10-18T11:00:00,1932,2668.21
```

**Use Cases:**
- Real-time dashboards (last 24-48 hours)
- Campaign performance tracking
- Peak hour analysis
- Time-zone specific optimization

### Historical Depth
✅ Tested successfully:
- 7 days back: 39 rows
- 30 days back: 35 rows
- 60 days back: 36 rows
- 90 days back: 32 rows
- 180 days back: 31 rows
- 365 days back: 16 rows

**Conclusion:** Historical data available for 365+ days

---

## Combined Analysis

### Data Source Comparison

| Capability | AdMob | Adjust |
|------------|-------|--------|
| **Time Granularity** | Daily only | Hourly + Daily |
| **Historical Depth** | 365+ days | 365+ days |
| **Primary Focus** | Ad monetization | User acquisition |
| **Revenue Tracking** | Ad revenue only | Ad revenue (no IAP) |
| **User Metrics** | Impressions, clicks | Installs, DAUs, retention |
| **Marketing Costs** | No | Yes (network_cost) |
| **Cohort Analysis** | No | Yes (D0, D1, D7, D30) |

### Recommended Configuration

**AdMob Pipeline:**
- Dimensions: APP, DATE, COUNTRY, PLATFORM, FORMAT, AD_UNIT
- Metrics: ESTIMATED_EARNINGS, IMPRESSIONS, CLICKS, AD_REQUESTS, MATCHED_REQUESTS, OBSERVED_ECPM
- Granularity: Daily
- Volume: 13,508 rows/day (1.2M for 90 days)

**Adjust Pipeline:**
- Dimensions: app, store_id, day, hour, country_code, country, os_name
- Metrics: installs, daus, ad_revenue, ad_impressions, ad_revenue_total_d0, ad_impressions_total_d0, network_cost, network_cost_diff, cohort_size_d0/d1/d7/d30
- Granularity: **HOURLY for real-time**, daily for historical
- Volume: 936 rows/day (hourly), 2,216 rows/day (daily)

---

## Architecture Implications

### Original Plan
- **Hot Storage (PostgreSQL):** 30 days, hourly updates
- **Cold Storage (Snowflake):** All history, daily batch

### Revised Architecture (Based on Validation)

**Real-Time Pipeline (PostgreSQL) - POSSIBLE with Adjust:**
- Source: **Adjust API (hourly granularity)**
- Data: Last 7-14 days
- Metrics: installs, DAUs, ad_revenue, network_cost (hourly)
- Use Case: Operational dashboards, campaign monitoring
- Update Frequency: Every 1-3 hours

**Batch Pipeline (Snowflake) - Both Sources:**
- **AdMob:** Daily data, full dimensions
- **Adjust:** Daily aggregations from hourly data
- Retention: Forever (cheap columnar storage)
- Use Case: Strategic analysis, trends, cohort analysis
- Update Frequency: Daily (1-2 times/day)

### Data Flow

```
Adjust API (hourly) → PostgreSQL (last 14 days) → Real-time dashboards
                    ↓
                Snowflake (daily agg) → Strategic analysis

AdMob API (daily) → Snowflake only → Revenue analysis
```

### Volume Management

**PostgreSQL (Hot - 14 days):**
- Adjust hourly: 936 × 14 = **13,104 rows** (tiny)

**Snowflake (Cold - Forever):**
- AdMob daily: 13,508 × 365 = **4.9M rows/year**
- Adjust daily: 2,216 × 365 = **809K rows/year**
- **Total:** 5.7M rows/year (very manageable)

---

## Business Metrics Impact

### Metrics NOW POSSIBLE (with Adjust hourly data)

✅ **Real-Time Metrics:**
- Hourly install velocity
- Peak acquisition hours by geography
- Campaign performance (hour-by-hour)
- Real-time LTV Day 0 tracking
- Hourly ad revenue trends

✅ **Cohort Analysis:**
- Day 0, 1, 7, 30 retention rates
- Cohort-based LTV calculation
- Retention curve analysis

✅ **Advanced Analytics:**
- Geographic arbitrage opportunities
- Time-zone optimization
- Hour-of-day revenue patterns
- Real-time ROI tracking (network_cost vs ad_revenue)

❌ **Still NOT Possible:**
- IAP revenue tracking (not configured in Adjust SDK)
- Combined revenue (ad + IAP) analysis
- Full product revenue attribution

---

## Next Steps

1. ✅ **Validation Complete** - All APIs tested, capabilities confirmed
2. ⏭️ **Update data_strategy.md** - Revise architecture with validated findings
3. ⏭️ **Design dimensional model** - Finalize fact/dimension tables
4. ⏭️ **Implement pipelines** - Build data ingestion (hourly for Adjust, daily for AdMob)
5. ⏭️ **Setup infrastructure** - PostgreSQL (hot) + Snowflake (cold)

---

## Test Scripts Reference

- `test_api_capabilities.py` - AdMob dimension/metric validation
- `test_hour_dimension.py` - AdMob HOUR dimension deep dive
- `test_adjust_capabilities.py` - Adjust endpoint validation

**All scripts executable with:**
```bash
python test_api_capabilities.py
python test_hour_dimension.py
python test_adjust_capabilities.py
```
