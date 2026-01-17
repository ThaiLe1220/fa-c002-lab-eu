# Mobile Analytics Data Strategy

**Purpose:** Metric formulas and calculation logic for the data warehouse.

**Related Docs:**
- `AI_AGENT_SPEC.md` - User context (who uses the system, what they need)
- `ARCHITECTURE.md` - Technical architecture (how the system works)
- This doc - **How to calculate metrics**

---

**Data Sources:**

- AdMob: Daily granularity (SOURCE OF TRUTH for revenue)
- Adjust: Daily granularity (attribution + D0 metrics + network costs)

**Key Metrics:**

- `ad_revenue_d0`, `ad_impressions_d0` - Day 0 metrics (70-80% of total)
- `network_cost` - Marketing spend for ROAS
- `paid_impressions` - UA impression count
- `subscrevnt_revenue` - Subscription revenue

---

## Table of Contents

1. [Business Problem & Value](#business-problem--value)
2. [ROAS: The North Star Metric](#roas-the-north-star-metric)
3. [The Four Pillars of ROAS](#the-four-pillars-of-roas)
4. [Revenue Reconciliation](#revenue-reconciliation)
5. [How This System Enables Better Decisions](#how-this-system-enables-better-decisions)
6. [Validated Data Sources](#validated-data-sources)
7. [Data Architecture](#data-architecture)
8. [Dimensional Model Design](#dimensional-model-design)
9. [Data Transformation Layers](#data-transformation-layers)
10. [Success Metrics](#success-metrics)

---

## Business Problem & Value

### Company Profile

- Mobile app publisher specializing in entertainment and productivity apps
- Primary revenue: In-app advertising (AdMob)
- Business model: Free apps with ad-supported monetization
- User behavior: High engagement on Day 0, high churn (typical for entertainment)
- Critical focus: **Day 0 metrics** (ROAS_D0, eCPM, IMPDAU_D0, CPI)

### Key Apps

- AI GPT Generator-Text to Video (`ai.video.generator.text.video`)
- Text to Video FLIX (`video.ai.videogenerator`)
- ~10 total apps across entertainment/productivity

### The Business Reality

```text
User Journey:
Day 0: Install app → Use features → Watch ads → Generate revenue
Day 1+: Either return (retention) → more revenue, OR delete app

Economics:
Spend money on user acquisition (Facebook/Google Ads)
Users generate money by watching ads (AdMob impressions)
Profit = Revenue generated - Acquisition cost
```

### Current Pain Points

- Manual Google Sheet workflow (export → append → analyze)
- No automated data quality checks (revenue mismatches go unnoticed)
- Limited historical analysis (only ~30-60 days retained)
- No alerting system (manual morning checks by UA team)
- Slow query performance (Google Sheets not optimized for analytics)

---

## ROAS: The North Star Metric

**ROAS = Revenue Generated / Money Spent on Ads**

```text
ROAS = 0.5 → Spent $100, got $50  → LOSING $50 (BAD!)
ROAS = 1.0 → Spent $100, got $100 → Breaking even
ROAS = 2.0 → Spent $100, got $200 → PROFIT $100 (GOOD!)
```

**Why ROAS is EVERYTHING:**

1. Tells you if marketing is profitable
2. Tells you which countries to invest in
3. Tells you which apps are worth promoting
4. Tells you when to STOP spending (if ROAS < 1.0)

**Real Example (Thailand, 2025-09-25):**

```text
App: AI Video Generator
network_cost = $1,406.09 (spent on user acquisition)
ad_revenue_total_D0 = $1,309.73 (earned from ads on Day 0)

ROAS_D0 = 1309.73 / 1406.09 = 0.93

Business Decision:
"We're losing $96 on Day 0. If D1+ retention doesn't recover this,
 we should reduce or pause Thailand campaign."
```

---

## The Four Pillars of ROAS

**VP/PO Business Logic: "ROAS depends on eCPM, IMPDAU_D0, and CPI"**

### 1. eCPM (Effective Cost Per Mille) = Revenue Efficiency

```text
eCPM = (admob_rev × 1000) / admob_imp
"How much money do we make per 1,000 ad impressions?"
```

**Example (Thailand):**

```text
admob_rev = $1,513.03
admob_imp = 67,679
eCPM = (1513.03 × 1000) / 67679 = $22.36

Interpretation: $22.36 per 1,000 impressions is EXCELLENT (typical: $5-15)
```

**Business Use:** Compare across countries, apps, and ad formats.

### 2. IMPDAU_D0 (Impressions Per DAU on Day 0) = Engagement

```text
IMPDAU_D0 = ad_impressions_total_D0 / daus
"How many ads does each user watch on their first day?"
```

**Example (Thailand):**

```text
ad_impressions_total_D0 = 57,559
daus = 14,608
IMPDAU_D0 = 57559 / 14608 = 3.94 impressions/user

Interpretation: Users watch ~4 ads on Day 0 - healthy engagement
```

**Business Use:** Product-market fit indicator, feature impact analysis.

### 3. CPI (Cost Per Install) = Acquisition Efficiency

```text
CPI = network_cost / installs
"How much does it cost to acquire one user?"
```

**Example (Thailand):**

```text
network_cost = $1,406.09
installs = 12,514
CPI = 1406.09 / 12514 = $0.112 (11.2 cents per install)

Interpretation: Very low CPI - efficient user acquisition
```

**Business Use:** Compare across countries, optimize bids, allocate budget.

### 4. The ROAS Formula

```text
ROAS_D0 = ad_revenue_total_D0 / network_cost

Mathematical relationship:
ROAS = (eCPM × IMPDAU_D0) / (CPI × 1000)

Intuition:
  High eCPM + High IMPDAU + Low CPI = High ROAS ✅
  Low eCPM + Low IMPDAU + High CPI = Low ROAS ❌
```

---

## Revenue Reconciliation

### The Two Data Sources Problem

**AdMob (Google) - SOURCE OF TRUTH for Revenue:**

- Tracks ad impressions and actual revenue
- Revenue = money that hits your bank account
- Definitive source for financial reporting

**Adjust (Attribution Platform) - ESTIMATES Revenue:**

- Tracks user acquisition (installs, campaigns, DAUs)
- SDK estimates revenue based on ad events
- Has network_cost (actual marketing spend)

### Why Mismatches Happen

1. **Timing differences**: AdMob reports when ad served, Adjust when user clicks
2. **Attribution windows**: Adjust might attribute revenue to wrong date/user
3. **SDK issues**: Adjust SDK might not fire correctly on all devices
4. **Data pipeline delays**: Adjust processes data slower than AdMob

### Real Example (Thailand, 2025-09-25)

```text
adjust_rev = $1,520.02
admob_rev  = $1,513.03
Difference = $7.00 (0.46% mismatch - ACCEPTABLE)

Impact on ROAS calculation:
Using Adjust: ROAS = 1.08 (looks profitable!)
Using AdMob:  ROAS = 1.076 (slightly less profitable)

Decision impact: Could over-invest if using wrong number
```

### System Requirement

- Automated daily comparison: adjust_rev vs admob_rev
- Flag mismatches > 5% with app/country/date details
- Alert mechanism: Notify UA team immediately
- Financial reporting: Always use AdMob revenue (source of truth)

---

## How This System Enables Better Decisions

### UA Team: Daily Operations

**Morning Workflow (5-10 minutes instead of 30+):**

1. **Revenue Reconciliation Dashboard** - Flag mismatches > 5%
2. **ROAS Performance by Country** - Identify campaigns to pause/scale
3. **Budget Allocation** - Find high ROAS + low CPI opportunities

**Example Alert:**

```text
🚨 Bangladesh - Text to Video FLIX
adjust_rev: $425 | admob_rev: $385 | mismatch: 10.4% (INVESTIGATE!)

Thailand: ROAS = 1.08 ✅ KEEP SPENDING
Egypt: ROAS = 0.42 🚨 PAUSE CAMPAIGN
```

### BOD: Strategic Planning

**Board Meeting Insights:**

1. **Portfolio Performance** - Top/bottom apps by revenue and ROAS
2. **Geographic Expansion** - High eCPM countries with low current spend
3. **Financial Forecasting** - Scale projections for profitable markets

### DEV Team: Product Development

1. **Feature Impact** - Week-over-week IMPDAU changes after releases
2. **Monetization Optimization** - High DAU but low IMPDAU = undermonetized
3. **Retention vs Monetization** - Balance ad frequency with user retention

### Automated Weekly Report

```text
Week 42 Performance Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 Overall:
Revenue: $48,250 (+8% vs last week)
Spend: $42,100 (+12% vs last week)
Net Profit: $6,150 (-15% vs last week) ⚠️

🏆 Top Countries:
Thailand: ROAS 1.08 (+3%) ✅
Vietnam: ROAS 1.15 (+18%) 🚀

⚠️ Watch List:
India: ROAS 0.72 (-18%) - investigate
Egypt: ROAS 0.42 (-25%) - consider pause
```

### Automated Alerts

| Alert Type | Trigger | Notify |
|------------|---------|--------|
| Revenue Mismatch | >5% adjust vs admob | UA team |
| ROAS Cliff | >15% drop in single day | UA + BOD |
| Budget Burn | >110% of daily budget | UA team |
| Data Freshness | >36 hours old | Data team |
| Profitability | ROAS < 0.8 for 3+ days | UA + Product |

---

## Validated Data Sources

### AdMob API - Ad Revenue (Daily Granularity)

**Confirmed Available:**

- **Dimensions:** APP, DATE, COUNTRY, PLATFORM, FORMAT, AD_UNIT
- **Metrics:** ESTIMATED_EARNINGS, IMPRESSIONS, CLICKS, AD_REQUESTS, MATCHED_REQUESTS, OBSERVED_ECPM
- **Volume:** 13,508 rows/day → 1.2M rows for 90 days
- **Historical Depth:** 365+ days

**NOT Available:** Hourly granularity, IAP revenue

### Adjust API - User Acquisition (Hourly + Daily)

**Confirmed Available:**

- **Dimensions:** app, store_id, day, hour, country_code, os_name
- **Metrics:** installs, daus, ad_revenue, ad_impressions, network_cost
- **Cohort Metrics:** cohort_size_d0, d1, d7, d30
- **Volume:** Daily 2,216 rows/day, Hourly 936 rows/day
- **Historical Depth:** 365+ days

**NOT Available:** IAP revenue (not configured in SDK)

---

## Data Architecture

### Hot vs Cold Storage

**Hot Storage (PostgreSQL) - Real-Time Operational**

- **Source:** Adjust API (hourly)
- **Retention:** Last 14 days
- **Update:** Every 1-3 hours
- **Volume:** 13,104 rows
- **Use Case:** Campaign monitoring, real-time dashboards

**Cold Storage (Snowflake) - Historical Analytics**

- **Source:** Both AdMob (daily) + Adjust (daily aggregations)
- **Retention:** Forever
- **Update:** Daily (1-2x/day)
- **Volume:** 5.7M rows/year
- **Use Case:** Strategic analysis, cohort retention, LTV modeling

### Data Flow

```text
Adjust API (hourly)
    ↓
PostgreSQL (last 14 days) → Real-time dashboards
    ↓ Archive daily
Snowflake (daily aggregations) → Strategic analysis

AdMob API (daily)
    ↓
Snowflake only → Revenue analysis
```

### Volume Summary

| Storage | Source | Rows/Year | Size |
|---------|--------|-----------|------|
| PostgreSQL | Adjust hourly | 13,104 (14 days) | <10 MB |
| Snowflake | AdMob daily | 4.9M | ~150 MB |
| Snowflake | Adjust daily | 809K | ~50 MB |

---

## Dimensional Model Design

### Design Philosophy

Start with business reality (current Google Sheet structure), then evolve.

### Current Google Sheet Structure (18 Columns)

```text
app, store_id, day, country_code, country, os_name,
install, daus, adjust_rev, adjust_imp,
ad_impressions_total_D0, ad_revenue_total_D0,
network_cost, adjust_cost, key,
admob_rev, admob_imp, paid_impressions
```

Everything pre-joined at daily grain by (app, country, day). This enables:

- ROAS: `admob_rev / network_cost`
- eCPM: `(admob_rev × 1000) / admob_imp`
- IMPDAU_D0: `ad_impressions_total_D0 / daus`
- CPI: `network_cost / install`

### Target: Star Schema

```text
        dim_dates               dim_countries
            │                        │
            │                        │
            └────────┐      ┌────────┘
                     │      │
         dim_apps ───┤ FACT ├──────────
                     │ TABLE│
                     └──────┘
         fct_app_daily_performance
```

### Fact Table: `fct_app_daily_performance`

**Grain:** One row per app, per date, per country, per platform

**Foreign Keys:**

- `date_key` → `dim_dates`
- `app_key` → `dim_apps`

**Metrics:**

| Source | Metrics |
|--------|---------|
| AdMob | ad_revenue, ad_impressions, ad_clicks, ad_ctr |
| Adjust | installs, clicks, daus |
| Adjust D0 | ad_revenue_d0, ad_impressions_d0 |
| Adjust Cost | network_cost, paid_impressions |
| Adjust Revenue | subscrevnt_revenue |

**Calculated:**

| Metric | Formula |
|--------|---------|
| d0_revenue_pct | ad_revenue_d0 / ad_revenue |
| total_revenue | ad_revenue + subscrevnt_revenue |
| revenue_per_install | total_revenue / installs |
| revenue_per_click | total_revenue / clicks |
| roas_d0 | ad_revenue / network_cost |
| ecpm | (ad_revenue × 1000) / ad_impressions |
| impdau_d0 | ad_impressions_d0 / daus |
| cpi | network_cost / installs |

### Dimension Tables

**`dim_dates`** (Type 1 SCD):

- date_key (PK), date, year, month, day, day_of_week, day_name

**`dim_apps`** (Type 1 SCD):

- app_key (PK), app_store_id, app_name

### Example Queries

**Yesterday's ROAS by country:**

```sql
SELECT
  c.country_name,
  SUM(f.ad_revenue) / NULLIF(SUM(f.network_cost), 0) as roas_d0
FROM fct_app_daily_performance f
JOIN dim_dates d ON f.date_key = d.date_key
WHERE d.date = CURRENT_DATE - 1
GROUP BY c.country_name
ORDER BY roas_d0 DESC;
```

**Revenue mismatch alert:**

```sql
SELECT app_name, country_code, date,
       adjust_revenue, admob_revenue,
       ABS(adjust_revenue - admob_revenue) / admob_revenue * 100 as mismatch_pct
FROM fct_daily_performance
WHERE mismatch_pct > 5.0
  AND date >= CURRENT_DATE - 7;
```

---

## Data Transformation Layers

### Overview: From API to Analytics

```text
Raw (API responses) → Staging (Clean) → Intermediate (Join + Calculate) → Mart (Star Schema)
```

### Layer 1: Raw

**Purpose:** Store API responses exactly as received.

**Tables:**

- `RAW_CAPSTONE.ADMOB_DAILY` - AdMob API dump
- `RAW_CAPSTONE.ADJUST_DAILY` - Adjust API dump

**Columns added:** `raw_record_id` (UUID), `batch_id`, `loaded_at`

### Layer 2: Staging

**Purpose:** Clean, standardize, validate.

**Models:**

- `stg_admob` - Type casting, column renaming, deduplication
- `stg_adjust` - Standardize to match AdMob naming

**Transformations:**

- Date string → DATE type
- Country codes → uppercase
- Platform → standardized (Android/iOS)
- NULL handling

**Tests:** unique, not_null on critical fields

### Layer 3: Intermediate

**Purpose:** Join sources, calculate business metrics.

**Model:** `int_app_daily_metrics`

**Join:** FULL OUTER JOIN on (app_store_id, date, country_code, platform)

**Calculations:**

```sql
revenue_per_install = ad_revenue / NULLIF(installs, 0)
revenue_per_click = ad_revenue / NULLIF(clicks, 0)
d0_revenue_pct = ad_revenue_d0 / NULLIF(ad_revenue, 0)
```

**Materialization:** Incremental table

### Layer 4: Mart

**Purpose:** Star schema for analytics.

**Models:**

- `dim_apps` - App dimension (MD5 surrogate key)
- `dim_dates` - Date dimension with calendar attributes
- `fct_app_daily_performance` - Fact table with foreign keys

**Custom Macro:** `calculate_ctr(clicks, impressions)`

**Tests:** relationships to dimensions, not_null on keys

### dbt Project Structure

```text
my_dbt_project/
├── models/
│   ├── 01_staging/
│   │   ├── stg_admob_midtest.sql
│   │   ├── stg_adjust_midtest.sql
│   │   └── _staging.yml
│   ├── 02_intermediate/
│   │   ├── int_app_daily_metrics.sql
│   │   └── _intermediate.yml
│   └── 03_mart/
│       ├── dim_apps.sql
│       ├── dim_dates.sql
│       ├── fct_app_daily_performance.sql
│       └── _mart.yml
├── macros/
│   └── calculate_ctr.sql
└── dbt_project.yml
```

---

## Success Metrics

### Data Quality

| Metric | Target |
|--------|--------|
| Revenue reconciliation | AdMob vs Adjust within 5% |
| Data freshness | <24 hours old |
| Test failures | Zero critical |
| Missing dates | None in 90-day period |

### Performance

| Metric | Target |
|--------|--------|
| Mart query response | <3 seconds |
| Daily pipeline run | <10 minutes (incremental) |
| Real-time updates | Within 2 hours |

### Business Enablement

- Answer all current analytics team questions
- ROAS calculation at country/app level
- Revenue reconciliation with alerting
- Week-over-week trend analysis
- Geographic arbitrage identification

### Key Formulas Reference

| Metric | Formula | Business Use |
|--------|---------|--------------|
| **ROAS** | ad_revenue / network_cost | Return on ad spend |
| **D0 Revenue %** | ad_revenue_d0 / ad_revenue | Same-day payback |
| **eCPM** | (ad_revenue / ad_impressions) × 1000 | Ad efficiency |
| **CPI** | network_cost / installs | Cost per install |
| **ARPDAU** | ad_revenue / daus | Revenue per active user |
| **IMPDAU_D0** | ad_impressions_d0 / daus | Day 0 engagement |
| **Total Revenue** | ad_revenue + subscrevnt_revenue | Full revenue picture |

---

## Revision History

| Date | Change |
|------|--------|
| Oct 2025 | Initial planning document for midterm |
| Nov 2025 | API validation complete, architecture finalized |
| Jan 2026 | Condensed for capstone, added D0 metrics, removed completed timeline |

**Status:** Foundation Complete - Ready for AI Agent Phase
