# Mobile Analytics Data Strategy - Complete Planning Document

**Project Goal:** Build a production-grade data warehouse that delivers real business value to mobile app publishers while passing mid-course test requirements.

**Status:** ✅ API Validation Complete + Business Requirements Validated (Oct 22, 2025)

**Success Criteria:**
- Pass mid-course test (70+ points minimum, targeting 80+)
- Replace manual Google Sheet workflow with automated data warehouse
- Enable BOD/UA/DEV teams to make data-driven decisions on ROAS optimization
- Provide daily operational metrics and weekly strategic analysis
- Industry-standard architecture and practices

**Key Findings from API Validation:**
- AdMob: Daily granularity only, 13.5K rows/day (SOURCE OF TRUTH for revenue)
- Adjust: **Hourly granularity available**, 936 rows/day (attribution + network costs)
- Cohort retention data available (D0, D1, D7, D30)
- IAP revenue NOT tracked

**Current State:**
- Data stored in Google Sheets (last week of previous month + current month)
- Manual exports from AdMob/Adjust APIs
- Looker Studio for visualization
- No automated quality checks or alerting

**Mid-Course Test Alignment:**
- ✅ **Real-Time Pipeline:** Adjust API (hourly) → PostgreSQL (Docker) → 936 rows/day
- ✅ **Batch Pipeline:** AdMob API (daily) → Snowflake → 13,500+ rows/batch (>> 500 requirement)
- ✅ **Architecture Justification:** Hot (operational) vs Cold (historical) storage for business needs

---

## Table of Contents

1. [Business Problem & Value](#business-problem--value)
2. [Validated Data Sources](#validated-data-sources)
3. [Data Architecture Overview](#data-architecture-overview)
4. [Data Transformation Layers](#data-transformation-layers)
5. [Dimensional Model Design](#dimensional-model-design)
6. [Execution Timeline](#execution-timeline)
7. [Success Metrics](#success-metrics)

---

## Business Problem & Value

### The Real-World Business Context

**Company Profile:**
- Mobile app publisher specializing in entertainment and productivity apps
- Primary revenue: In-app advertising (AdMob)
- Business model: Free apps with ad-supported monetization
- User behavior: High engagement on Day 0, high churn (typical for entertainment)
- Critical focus: **Day 0 metrics** (ROAS_D0, eCPM, IMPDAU_D0, CPI)

**Key Apps:**
- AI GPT Generator-Text to Video (`ai.video.generator.text.video`)
- Text to Video FLIX (`video.ai.videogenerator`)
- ~10 total apps across entertainment/productivity

**The Business Reality:**
```
User Journey:
Day 0: Install app → Use features → Watch ads → Generate revenue
Day 1+: Either return (retention) → more revenue, OR delete app

Economics:
Spend money on user acquisition (Facebook/Google Ads)
Users generate money by watching ads (AdMob impressions)
Profit = Revenue generated - Acquisition cost
```

**Current Pain Points:**
- Manual Google Sheet workflow (export → append → analyze)
- No automated data quality checks (revenue mismatches go unnoticed)
- Limited historical analysis (only ~30-60 days retained)
- No alerting system (manual morning checks by UA team)
- Slow query performance (Google Sheets not optimized for analytics)
- Error-prone manual processes (copy-paste mistakes, schema drift)

### The North Star Metric: ROAS (Return On Ad Spend)

**ROAS = Revenue Generated / Money Spent on Ads**

```
ROAS = 0.5 → Spent $100, got $50  → LOSING $50 (BAD!)
ROAS = 1.0 → Spent $100, got $100 → Breaking even
ROAS = 2.0 → Spent $100, got $200 → PROFIT $100 (GOOD!)
ROAS = 5.0 → Spent $100, got $500 → JACKPOT!
```

**Why ROAS is EVERYTHING:**
1. Tells you if marketing is profitable
2. Tells you which countries to invest in
3. Tells you which apps are worth promoting
4. Tells you when to STOP spending (if ROAS < 1.0)

**Real Example from Data (Thailand, 2025-09-25):**
```
App: AI Video Generator
network_cost = $1,406.09 (spent on user acquisition)
ad_revenue_total_D0 = $1,309.73 (earned from ads on Day 0)

ROAS_D0 = 1309.73 / 1406.09 = 0.93

Business Decision:
"We're losing $96 on Day 0. If D1+ retention doesn't recover this,
 we should reduce or pause Thailand campaign."
```

### The Four Pillars of ROAS

**VP/PO Business Logic: "ROAS depends on eCPM, IMPDAU_D0, and CPI"**

#### 1. eCPM (Effective Cost Per Mille) = Revenue Efficiency

```
eCPM = (admob_rev × 1000) / admob_imp

"How much money do we make per 1,000 ad impressions?"
```

**Real Example (Thailand):**
```
admob_rev = $1,513.03
admob_imp = 67,679

eCPM = (1513.03 × 1000) / 67679 = $22.36

Interpretation: $22.36 per 1,000 impressions is EXCELLENT for entertainment
(typical range: $5-15)
```

**Business Use:**
- Compare across countries: India eCPM vs US eCPM
- Compare across apps: Which app monetizes better?
- Optimize ad placements: Which formats have highest eCPM?

#### 2. IMPDAU_D0 (Impressions Per DAU on Day 0) = Engagement

```
IMPDAU_D0 = ad_impressions_total_D0 / daus

"How many ads does each user watch on their first day?"
```

**Real Example (Thailand):**
```
ad_impressions_total_D0 = 57,559
daus = 14,608

IMPDAU_D0 = 57559 / 14608 = 3.94 impressions/user

Interpretation: Users watch ~4 ads on Day 0 - healthy engagement
```

**Business Use:**
- Product-market fit indicator (higher = better engagement)
- Compare across countries: Which markets engage more?
- Feature impact: Did new features increase/decrease IMPDAU?

#### 3. CPI (Cost Per Install) = Acquisition Efficiency

```
CPI = network_cost / installs

"How much does it cost to acquire one user?"

Also: CPI = CPM × IPM / 1000
Where:
  CPM = (network_cost × 1000) / paid_impressions
  IPM = (installs × 1000) / paid_impressions
```

**Real Example (Thailand):**
```
network_cost = $1,406.09
installs = 12,514

CPI = 1406.09 / 12514 = $0.112 (11.2 cents per install)

Interpretation: Very low CPI - efficient user acquisition
```

**Business Use:**
- Compare across countries: Where is acquisition cheapest?
- Ad network optimization: Adjust bids to hit target CPI
- Budget allocation: Invest more where CPI is low

#### 4. The ROAS Formula (Putting It Together)

```
ROAS_D0 = ad_revenue_total_D0 / network_cost

Mathematical relationship:
ROAS = (eCPM × IMPDAU_D0) / (CPI × 1000)

Intuition:
  High eCPM + High IMPDAU + Low CPI = High ROAS ✅
  Low eCPM + Low IMPDAU + High CPI = Low ROAS ❌
```

**Thailand Example Validation:**
```
eCPM = $22.36
IMPDAU_D0 = 3.94
CPI = $0.112

Predicted ROAS = (22.36 × 3.94) / (0.112 × 1000) = 0.79
Actual ROAS = 0.93

(Close - small differences due to calculation timing)
```

### Critical: Revenue Reconciliation (Data Quality Foundation)

**The Two Data Sources Problem:**

**AdMob (Google) - SOURCE OF TRUTH for Revenue:**
- Tracks ad impressions and actual revenue
- Revenue = money that hits your bank account
- Updated daily
- Definitive source for financial reporting

**Adjust (Attribution Platform) - ESTIMATES Revenue:**
- Tracks user acquisition (installs, campaigns, DAUs)
- SDK estimates revenue based on ad events
- Has network_cost (actual marketing spend)
- Revenue is calculated/estimated, not actual

**Why Mismatches Happen:**
1. **Timing differences**: AdMob reports when ad served, Adjust when user clicks
2. **Attribution windows**: Adjust might attribute revenue to wrong date/user
3. **SDK issues**: Adjust SDK might not fire correctly on all devices
4. **Data pipeline delays**: Adjust processes data slower than AdMob

**Real Example (Thailand, 2025-09-25):**
```
adjust_rev = $1,520.02
admob_rev  = $1,513.03

Difference = $7.00 (0.46% mismatch - ACCEPTABLE)

Impact on ROAS calculation:
Using Adjust: ROAS = 1520.02 / 1406.09 = 1.08 (looks profitable!)
Using AdMob:  ROAS = 1513.03 / 1406.09 = 1.076 (slightly less profitable)

Decision impact: Could over-invest if using wrong number
```

**UA Team Daily Workflow Need:**
1. **Morning check**: Revenue reconciliation dashboard
2. **Alert trigger**: When mismatch > 5%
3. **Investigation**: Check which app/country has mismatch
4. **Action**: Verify Adjust SDK, check attribution, re-sync data
5. **Financial reporting**: Always use AdMob revenue (source of truth)

**System Requirement:**
- Automated daily comparison: adjust_rev vs admob_rev
- Flag mismatches > 5% with app/country/date details
- Historical tracking: Has this country/app had consistent mismatches?
- Alert mechanism: Notify UA team immediately

### What Your Analytics Team Currently Tracks

Your existing analytics team focuses on these daily metrics:

**Acquisition Metrics:**
- Install counts by country and campaign
- Marketing spend (network cost)
- Cost per install calculations

**Immediate Monetization:**
- Day 0 revenue (first-day earnings from new users)
- Day 0 ad impressions
- Immediate return on ad spend

**Engagement Indicators:**
- Daily Active Users (DAU)
- DAU to Install ratio (proxy for retention)

**Data Quality Checks:**
- AdMob revenue vs Adjust revenue reconciliation
- Impression count matching between platforms

**What's Missing (Your Opportunity):**
- Automated revenue reconciliation with alerting
- Week-over-week trend analysis ("this week vs last week")
- Geographic arbitrage opportunities (same app, different countries)
- Cross-app performance comparison (which app is winning?)
- Dangerous signal detection (ROAS drops, revenue mismatches)
- Historical context beyond 30-60 days

---

## How This System Enables Better Decisions

### UA Team: Daily Operations

**Morning Workflow (5-10 minutes instead of 30+ minutes):**

1. **Revenue Reconciliation Dashboard**:
   ```sql
   Query: "Yesterday's adjust_rev vs admob_rev by app/country"

   Alert Example:
   ⚠️ India - AI Video Generator
   adjust_rev: $502 | admob_rev: $479 | mismatch: 4.8% (OK)

   🚨 Bangladesh - Text to Video FLIX
   adjust_rev: $425 | admob_rev: $385 | mismatch: 10.4% (INVESTIGATE!)

   Action: Check Adjust SDK for Bangladesh, verify attribution
   ```

2. **ROAS Performance by Country**:
   ```sql
   Query: "Yesterday's ROAS_D0 by country, flagged if < 1.0"

   Thailand: ROAS = 1.08 ✅ KEEP SPENDING ($1406/day budget)
   India: ROAS = 0.72 ⚠️ REVIEW (might need D1 data)
   Egypt: ROAS = 0.42 🚨 PAUSE CAMPAIGN (losing $58 per day)

   Decision: Reduce Egypt budget from $138/day to $50/day (test)
   ```

3. **Budget Allocation Optimization**:
   ```sql
   Query: "Which countries have ROAS > 1.5 AND CPI < $0.20?"

   Result: Thailand (ROAS=1.08, CPI=$0.11), Brazil (ROAS=1.04, CPI=$0.11)

   Decision: Increase Thailand budget from $1400 to $2000/day
   ```

4. **Campaign Performance Alerts**:
   ```sql
   Query: "Any country with >20% ROAS drop vs yesterday?"

   Alert: India ROAS dropped from 0.85 to 0.72 (-15%)
   Possible causes: Holiday? Competitor campaign? Check logs

   Decision: Monitor for 1 more day before action
   ```

### BOD: Strategic Planning (Monthly/Quarterly)

**Board Meeting Insights (Previously impossible with Google Sheets):**

1. **Portfolio Performance View**:
   ```sql
   Query: "Last 90 days - top 5 apps by revenue, bottom 5 by ROAS"

   Top Performers:
   1. AI Video Generator: $142K revenue, ROAS 1.05
   2. Text to Video FLIX: $85K revenue, ROAS 0.98

   Bottom Performers:
   4. [App Name]: $12K revenue, ROAS 0.42
   5. [App Name]: $8K revenue, ROAS 0.35

   Decision: Sunset bottom 2 apps, redirect budget to top performers
   ```

2. **Geographic Expansion Opportunities**:
   ```sql
   Query: "Countries with high eCPM (>$15) but low current spend (<$500/day)"

   Philippines: eCPM=$18, current spend=$200/day, ROAS=1.15

   Opportunity: Test $2000/day budget for 2 weeks
   Projected revenue increase: $3,600/day if ROAS holds

   Decision: Approve $20K test budget for Philippines expansion
   ```

3. **Product Roadmap Prioritization**:
   ```sql
   Query: "IMPDAU_D0 trends - which apps have best engagement?"

   AI Video Generator: IMPDAU=4.2 (users love it, watch lots of ads)
   Text to Video FLIX: IMPDAU=2.8 (lower engagement)

   Decision: Prioritize features for AI Video Generator (proven engagement)
   ```

4. **Financial Forecasting**:
   ```sql
   Query: "If we scale Thailand & Brazil by 2x (maintain current ROAS), projected revenue?"

   Current: Thailand $1513/day + Brazil $814/day = $2327/day
   Scaled 2x: $4654/day revenue, $4200/day cost
   Net profit: $454/day → $13,620/month additional profit

   Decision: Approve budget increase, hire 1 more UA specialist
   ```

### DEV Team: Product Development

**Feature Impact Validation:**

1. **New Feature A/B Testing**:
   ```sql
   Scenario: Added new video templates last week

   Query: "Week-over-week IMPDAU_D0 change for AI Video Generator"

   Before: IMPDAU=3.5
   After: IMPDAU=4.2 (+20%)

   Validation: New templates increased engagement significantly
   Decision: Build 10 more similar templates this sprint
   ```

2. **Monetization Optimization**:
   ```sql
   Query: "Countries with high DAU but low IMPDAU - undermonetized"

   India: DAU=24,534, IMPDAU=2.1 (users not seeing enough ads)
   Thailand: DAU=14,608, IMPDAU=3.9 (well monetized)

   Decision: Add natural ad placements in India version
   ```

3. **Retention vs Monetization Tradeoff**:
   ```sql
   Query: "Apps with ROAS_D0 < 1.0 but D7 retention > 30%"

   Text to Video FLIX: ROAS_D0=0.98, D7 retention=35%

   Analysis: Users come back, LTV will recover D0 loss
   Decision: Don't increase ads (will hurt retention), keep current balance
   ```

### The Weekly Report (Automated)

**"This Week vs Last Week" Analysis:**

```
Week 42 Performance Summary (Oct 14-20, 2025)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 Overall Metrics:
Revenue: $48,250 (+8% vs last week)
Marketing Spend: $42,100 (+12% vs last week)
Net Profit: $6,150 (-15% vs last week) ⚠️

🏆 Top Performing Countries:
Thailand: ROAS 1.08 (+3% vs last week) ✅
Brazil: ROAS 1.04 (stable)
Vietnam: ROAS 1.15 (+18% vs last week) 🚀

⚠️ Countries to Watch:
India: ROAS 0.72 (-18% vs last week) - investigate
Egypt: ROAS 0.42 (-25% vs last week) - consider pause

📱 App Performance:
AI Video Generator: $28K revenue (+12%)
Text to Video FLIX: $15K revenue (+5%)

🎯 Recommended Actions:
1. Investigate India ROAS drop (competitor activity?)
2. Pause or reduce Egypt campaign
3. Increase Thailand/Vietnam budgets (+20%)
4. Test Philippines expansion ($2K/day for 2 weeks)
```

### Dangerous Signal Detection (Automated Alerts)

**System should flag these scenarios automatically:**

1. **Revenue Mismatch Alert**:
   - Any country/app with >5% adjust_rev vs admob_rev difference
   - Notify: UA team immediately via Telegram

2. **ROAS Cliff Alert**:
   - Any country with >15% ROAS drop in single day
   - Notify: UA team + BOD

3. **Budget Burn Alert**:
   - Any campaign spending >110% of daily budget
   - Notify: UA team

4. **Data Freshness Alert**:
   - If latest data is >36 hours old
   - Notify: Data team (YOU!)

5. **Profitability Alert**:
   - Any app with ROAS < 0.8 for 3+ consecutive days
   - Notify: UA team + Product team

---

## Validated Data Sources

### AdMob API - Ad Revenue (Daily Granularity)

✅ **Confirmed Available:**
- **Dimensions:** APP, DATE, COUNTRY, PLATFORM, FORMAT, AD_UNIT
- **Metrics:** ESTIMATED_EARNINGS, IMPRESSIONS, CLICKS, AD_REQUESTS, MATCHED_REQUESTS, OBSERVED_ECPM
- **Granularity:** Daily only (HOUR dimension NOT available)
- **Volume:** 13,508 rows/day → 1.2M rows for 90 days
- **Historical Depth:** 365+ days

❌ **NOT Available:**
- Hourly time granularity
- IAP revenue tracking

**Use Case:** Daily revenue analysis, ad format performance, platform comparison

### Adjust API - User Acquisition (Hourly + Daily)

✅ **Confirmed Available:**
- **Dimensions:** app, store_id, day, **hour**, country_code, country, os_name
- **Metrics:** installs, daus, ad_revenue, ad_impressions, network_cost, network_cost_diff
- **Cohort Metrics:** cohort_size_d0, cohort_size_d1, cohort_size_d7, cohort_size_d30
- **Granularity:** **HOURLY available** (936 rows/day)
- **Volume:** Daily 2,216 rows/day, Hourly 936 rows/day
- **Historical Depth:** 365+ days

❌ **NOT Available:**
- IAP revenue (not configured in SDK)

**Use Case:** Real-time acquisition tracking, cohort retention, marketing ROI, hourly trends

---

## Data Architecture Overview

### Validated Architecture: Hot vs Cold Storage

**Hot Storage (PostgreSQL) - Real-Time Operational**
- **Source:** Adjust API only (hourly granularity)
- **Data Retained:** Last 14 days
- **Update Frequency:** Every 1-3 hours
- **Metrics:** Hourly installs, DAUs, ad_revenue, network_cost
- **Volume:** 936 × 14 = 13,104 rows (tiny)
- **Use Case:** "What's happening RIGHT NOW?"
- **Who Uses It:** Operations team, campaign monitoring, real-time dashboards

**Cold Storage (Snowflake) - Historical Analytics**
- **Source:** Both AdMob (daily) + Adjust (daily aggregations)
- **Data Retained:** Forever
- **Update Frequency:** Daily (1-2x/day)
- **Volume:** 5.7M rows/year (very manageable)
- **Use Case:** "What patterns exist over time?"
- **Who Uses It:** Strategic analysis, cohort retention, LTV modeling

### Revised Data Flow

```
Adjust API (hourly)
    ↓
PostgreSQL (last 14 days) → Real-time dashboards
    ↓ Archive daily
Snowflake (daily aggregations) → Strategic analysis

AdMob API (daily)
    ↓
Snowflake only → Revenue analysis
```

### Why This Architecture?

**Real-Time Pipeline (PostgreSQL + Adjust hourly):**
- Campaign manager sees install spike at 2pm → increase budget NOW
- Hourly ROI drops below threshold → pause campaign immediately
- Peak hour analysis: installs highest 8pm-11pm in India
- Real-time arbitrage: Brazil installs cheaper during morning hours

**Batch Pipeline (Snowflake + both sources):**
- CFO asks "What was Q3 revenue growth?"
- Product team: "Which countries have best 30-day retention?"
- Data scientist builds LTV model using 6 months cohort data
- Marketing: "Compare AdMob revenue vs Adjust ad_revenue for reconciliation"

**Archive Process:**
- Every night, Adjust hourly data aggregated to daily → Snowflake
- PostgreSQL stays fast (14 days only)
- Snowflake stores everything forever (cheap)
- AdMob data goes straight to Snowflake (daily already)

---

## Validated Data Volumes

✅ **API validation complete** - See `api_validation_results.md` for full details

### AdMob - Actual Volumes (Tested Oct 18, 2025)

**Configuration:** APP, DATE, COUNTRY, PLATFORM, FORMAT, AD_UNIT

**Actual Data:**
- Basic (no FORMAT/AD_UNIT): 1,644 rows/day
- With FORMAT: 5,127 rows/day
- Full dimensions: **13,508 rows/day**

**90-Day Projection:**
- 13,508 × 90 = **1,215,720 rows** (1.2M)

**Historical Depth:** 365+ days confirmed

### Adjust - Actual Volumes (Tested Oct 18, 2025)

**Daily Granularity:**
- Full dimensions: **2,216 rows/day**
- 90-day projection: 199,440 rows

**Hourly Granularity:**
- app, day, hour: **936 rows/day**
- 90-day projection: 84,240 rows

**Historical Depth:** 365+ days confirmed

### Combined Storage Requirements

**PostgreSQL (Hot - 14 days):**
- Adjust hourly: 936 × 14 = **13,104 rows** (negligible)
- Storage: <10 MB

**Snowflake (Cold - Forever):**
- AdMob daily: 13,508 × 365 = **4.9M rows/year**
- Adjust daily: 2,216 × 365 = **809K rows/year**
- **Total:** 5.7M rows/year
- Storage: ~200 MB/year (compressed columnar)

**Conclusion:** Volumes are SMALL by industry standards, easily manageable

---

## Data Collection Orchestration Strategy

**Decision Date:** October 27, 2025

### Orchestration Approach: GitHub Actions Scheduled Workflows

**Selected Solution:**
```yaml
# .github/workflows/data_collection.yml
on:
  schedule:
    - cron: '0 2 * * *'    # AdMob daily at 2 AM UTC
    - cron: '0 * * * *'    # Adjust hourly
  workflow_dispatch:        # Manual trigger for demo/testing
```

**Why GitHub Actions:**
1. **Already in stack** - CI/CD requirement for test (5 pts)
2. **Zero additional infrastructure** - No servers to manage
3. **Free** - Included in GitHub free tier
4. **Easy to demonstrate** - Show workflow runs during test
5. **Industry-standard** - Used by many production data pipelines

**Execution Pattern:**
- **AdMob Pipeline:** Runs daily at 2 AM UTC
  - Fetches previous day's data (13,500+ rows)
  - Loads to Snowflake RAW.ADMOB_DAILY
  - Execution time: ~2-3 minutes

- **Adjust Pipeline:** Runs every hour on the hour
  - Fetches previous hour's data (~39 rows)
  - Loads to Snowflake RAW.ADJUST_HOURLY
  - Execution time: ~1 minute

- **dbt Transformations:** Runs after data collection
  - Triggered by workflow completion
  - Incremental models process only new data
  - Execution time: ~5 minutes

**Alternatives Considered:**

| Solution | Pros | Cons | Decision |
|----------|------|------|----------|
| **Cron Jobs** | Simple, native Linux | Requires 24/7 server ($$$), no monitoring | ❌ Rejected |
| **Apache Airflow** | Enterprise-grade, powerful | Overkill for 2 pipelines, complex setup | ❌ Rejected |
| **dbt Cloud** | Built-in scheduler | Paid service, handles dbt only (not data collection) | ❌ Rejected |
| **GitHub Actions** | Free, already in stack, easy demo | Execution time limits (6 hrs max) | ✅ Selected |

**Mid-Course Test Strategy:**
- **Manual execution acceptable** for demonstration
- **Scheduled workflows = bonus points** (shows production thinking)
- **Focus:** Pipeline correctness > automation complexity
- **Demo approach:** Run scripts manually, explain scheduled workflow in documentation

**Production Deployment Considerations:**
- GitHub Actions limits: 2,000 minutes/month (free tier) = ~67 hours
- Our usage: (1 min × 24 runs/day) + (3 min × 1 run/day) = ~30 min/day = 900 min/month
- **Conclusion:** Well within free tier limits for production use

**Monitoring & Alerting:**
- GitHub Actions provides email notifications on workflow failures
- Can integrate with Slack/Discord for real-time alerts
- Workflow run history provides audit trail

**Future Enhancements (Post-Test):**
- Add retry logic for API failures
- Implement exponential backoff for rate limiting
- Add data quality checks before loading
- Integrate with monitoring tools (DataDog, New Relic)

---

## Mid-Course Test Requirements Mapping

### Real-Time Pipeline (Section 1: 20 points)

**Test Requirement:**
> "Real-Time (Streaming) Pipeline Script: Simulates row-by-row data ingestion, collects data from API or streaming source, must demonstrate incremental data collection"

**Your Implementation:**
```python
# Script: scripts/collect_adjust_realtime.py
# Source: Adjust API (hourly granularity)
# Destination: PostgreSQL (Docker container)
# Pattern: Row-by-row incremental ingestion
```

**Why This Qualifies:**
- ✅ **API Source:** Adjust API provides hourly data (936 rows/day = ~39 rows/hour)
- ✅ **Incremental:** Each hour = new batch of rows by (app, country, hour_timestamp)
- ✅ **Row-by-Row:** Script processes each API response row individually into PostgreSQL
- ✅ **Fresh Data:** Timestamps prove data collected during demo (`loaded_at = NOW()`)
- ✅ **Operational Use Case:** Hot storage for real-time campaign monitoring (last 14 days)

**Demo Script:**
```bash
# Show PostgreSQL running in Docker
docker ps | grep postgres

# Execute real-time collection
python scripts/collect_adjust_realtime.py --hours 1

# Output shows row-by-row ingestion:
# ✓ Inserted: AI Video Generator | Thailand | 2025-10-22 14:00:00
# ✓ Inserted: AI Video Generator | Vietnam | 2025-10-22 14:00:00
# ... (39 rows total for last hour)

# Query PostgreSQL showing FRESH data
psql -d mobile_analytics -c "
  SELECT app, country, hour_timestamp, installs, revenue, loaded_at
  FROM adjust_hourly
  WHERE loaded_at >= NOW() - INTERVAL '5 minutes'
  ORDER BY loaded_at DESC
  LIMIT 10;"

# Timestamps prove data is NEW (collected seconds ago)
```

---

### Batch Pipeline (Section 1: 20 points)

**Test Requirement:**
> "Batch Pipeline Script: Ingests data in batches, each batch must contain ≥500 rows, must demonstrate batch processing capability"

**Your Implementation:**
```python
# Script: scripts/collect_admob_batch.py
# Source: AdMob API (daily granularity)
# Destination: Snowflake
# Pattern: Daily batches of 13,500+ rows
```

**Why This Qualifies:**
- ✅ **Batch Size:** 13,508 rows per day (27x the 500-row requirement!)
- ✅ **Batch Processing:** Processes entire day at once, not row-by-row
- ✅ **Multiple Batches:** Can collect 7 days = 7 batches = ~94,000 total rows
- ✅ **Fresh Data:** Timestamps in Snowflake prove data collected during demo
- ✅ **Historical Use Case:** Cold storage for strategic analysis (forever retention)

**Demo Script:**
```bash
# Execute batch collection
python scripts/collect_admob_batch.py --days 7

# Output shows batch processing:
# 📦 Fetching batch for 2025-10-22...
#    Batch size: 13,508 rows
#    ✓ Loaded 13,508 rows to Snowflake
# 📦 Fetching batch for 2025-10-21...
#    Batch size: 13,487 rows
#    ✓ Loaded 13,487 rows to Snowflake
# ...
# ✅ Total: 94,638 rows loaded (7 batches)
#    Average batch size: 13,520 rows

# Query Snowflake showing FRESH data
SELECT DATE(date) as report_date,
       COUNT(*) as row_count,
       SUM(admob_revenue) as total_revenue,
       MAX(loaded_at) as last_loaded
FROM raw.admob_daily
WHERE loaded_at >= CURRENT_DATE - 1
GROUP BY DATE(date)
ORDER BY report_date DESC;

# Last_loaded column shows fresh timestamps
```

---

### PostgreSQL Docker (Section 1: 5 points)

**Test Requirement:**
> "PostgreSQL database running via Docker containerization, database accessible and operational during demo"

**Your Implementation:**
```yaml
# File: docker-compose.yml
services:
  postgres:
    image: postgres:15
    container_name: mobile_analytics_db
    environment:
      POSTGRES_DB: mobile_analytics
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
```

**Demo Script:**
```bash
# Start Docker container
docker-compose up -d

# Verify running
docker ps
# Shows: mobile_analytics_db running on port 5432

# Test connection
psql -h localhost -p 5432 -U postgres -d mobile_analytics -c "SELECT version();"
# Returns PostgreSQL version confirming connectivity

# Show table exists
psql -d mobile_analytics -c "\dt"
# Lists: adjust_hourly table with schema
```

---

### Business Justification: Why This Architecture?

**Hot Storage (PostgreSQL - Real-Time):**
- Operations team monitors campaigns **hourly** during high-spend days
- Detect install spikes or ROAS drops **within hours**, not next day
- PostgreSQL optimized for **fast transactional queries** (filter by last 24 hours)
- 14-day retention sufficient for operational decisions

**Cold Storage (Snowflake - Batch):**
- AdMob API **only provides daily granularity** (technical limitation, not choice)
- Revenue is **source of truth** - needs permanent historical storage for audits
- Snowflake optimized for **analytical aggregations** (month-over-month trends, cohort analysis)
- Forever retention for BOD strategic planning

**This Isn't Artificial - This IS How Mobile Analytics Actually Works:**
- User acquisition tracked **hourly** (bidding adjustments happen intra-day)
- Revenue reconciliation happens **daily** (bank transfers, reporting, audits)
- Standard industry pattern: hot operational database + cold analytical warehouse

---

**Why this matters:**
- Confirms our storage and processing time estimates
- Identifies if volume is bigger than expected (need optimization)
- Helps plan database partitioning strategy

**Validation Step 3: Data Quality Assessment**

This is the CRITICAL step. Bad data = bad business decisions = real money lost.

Fetch the last 7 days of data and run these quality checks:

**Completeness Checks:**
- Are there any missing dates in the 7-day range?
- Do all apps report data every day, or are there gaps?
- Are there apps with zero revenue for multiple days? (Dead apps or data issue?)
- Are all expected countries present?

**Consistency Checks:**
- Compare AdMob revenue to Adjust revenue for same app/date/country
- Expected: Within 5% difference (normal attribution timing differences)
- If difference is greater than 20%: Data quality problem or timezone mismatch
- Compare impression counts between AdMob and Adjust
- Check if DAU counts make sense (DAUs shouldn't wildly fluctuate without reason)

**Data Grain Verification:**
- Is hourly data actually available for all metrics?
- Or is some data only available at daily level?
- Can we join AdMob and Adjust at hourly granularity? Or only daily?
- This determines if real-time pipeline can truly be hourly

**Duplicate Detection:**
- Are there duplicate rows (same app + date + country appearing twice)?
- If yes: API bug or script running multiple times?
- Need deduplication logic in staging layer

**NULL Value Analysis:**
- Which fields have NULLs?
- Are NULLs expected (no activity) or data errors?
- Example: NULL impressions but non-NULL revenue = data error
- Example: NULL revenue in small country = probably no activity

**Timezone Consistency:**
- AdMob uses UTC timestamps
- Adjust may use app-specific timezones
- For same "date", do totals match?
- If not: need timezone normalization in staging layer

**Business Logic Validation:**
- Check if DAU > Installs on same day (expected - includes returning users)
- Check if any negative revenue (impossible - data error)
- Check if eCPM is reasonable ($0.10 to $20 typical, $100+ suspicious)
- Check if CPI is reasonable ($0.01 to $5 typical for most countries)

**Expected Outcomes:**
- List of data quality issues discovered
- Severity rating (critical vs acceptable)
- Decision: Is this data trustworthy enough for business decisions?
- Action plan: What needs to be cleaned or fixed?

**Example Quality Issues You Might Find:**

*Issue:* "AdMob shows $100 revenue for App X in Luxembourg, but Adjust shows $5"
*Severity:* High - 20x discrepancy
*Action:* Investigate timezone differences, check if this is consistent across days

*Issue:* "App Y has no data for Brazil on Oct 15"
*Severity:* Low - probably app wasn't active there yet
*Action:* Document as expected, not a data error

*Issue:* "Same row appears twice with different loaded_at timestamps"
*Severity:* Medium - causes incorrect totals
*Action:* Add deduplication logic based on unique key

---

### Phase 1: "Can We Clean The Fucking Data?"

Once we know what issues exist, design the cleaning strategy.

**Data Issue Categories and Solutions:**

**Category 1: Missing Data**

Problem examples:
- App X never launched in Country Y, so no data exists (expected)
- API was down on Oct 10, so that day's data missing (unexpected)
- Hourly data has gaps (API limitation?)

Solution approach:
- Flag truly missing data vs "no activity"
- Decide: Backfill if possible, or accept gaps?
- Document known gaps so analysts aren't confused

**Category 2: Duplicate Data**

Problem examples:
- Re-running ingestion script creates duplicate rows
- API occasionally returns same data twice

Solution approach:
- Define unique key for each row: (app_id, date, country, platform, hour, ad_unit)
- Use UPSERT logic in staging layer: If row with same key exists, UPDATE it. Otherwise INSERT new row.
- This makes pipeline idempotent (safe to run multiple times)

**Category 3: Data Type Mismatches**

Problem examples:
- Revenue comes as string "12.34" instead of decimal number
- Date comes as string "2025-01-01" instead of DATE type
- NULL vs 0 confusion (is NULL missing data or zero activity?)

Solution approach in staging layer:
- Explicitly CAST all fields to correct types
- Convert string dates to DATE type
- Decide NULL handling: Convert to 0 for metrics? Or keep as NULL and handle in queries?
- Validate: Revenue must be >= 0 (can't be negative)

**Category 4: Business Logic Validation**

Problem examples:
- DAU count is higher than Installs on same day (actually expected - retained users + new users)
- Revenue discrepancy: AdMob $100, Adjust $95 (which is source of truth?)
- Negative ROI (could be real - losing money on campaign)

Solution approach:
- Document which scenarios are "expected business reality" vs "data errors"
- Create validation rules that flag suspicious records for manual review
- Example: If revenue discrepancy > 20%, flag for investigation
- Example: If eCPM > $50, flag as suspicious (might be real, might be error)

**Staging Layer Validation Strategy:**

For every staging model, implement automated tests that run with every dbt execution:

Tests to include:
- **not_null test:** Critical fields cannot be NULL (date, app_id, revenue)
- **unique test:** Unique key combinations shouldn't duplicate
- **accepted_range test:** Revenue between $0 and $10,000 per row (flag outliers)
- **recency test:** Latest data should be less than 2 days old (catch pipeline failures)
- **relationship test:** Every app_id in fact table must exist in dim_app
- **expression_is_true test:** Custom business logic (e.g., "DAU >= 0")

Why automated testing matters:
- Catches data quality issues BEFORE bad data reaches business users
- Every dbt run validates data automatically
- Alerts sent if tests fail (email, Slack notification)
- Prevents bad data from corrupting downstream marts

---

### Phase 2: "How Do We Handle The Fucking Volume?"

With millions of rows, naive approaches fail. Industry-standard optimizations required.

**Challenge 1: Incremental Loading**

**The Problem:**
- Day 1: Load 90 days of history (4 million rows) - takes 10 minutes
- Day 2: Re-load all 90 days again? (wasteful - 99% is unchanged data)
- Naive approach: 10 minutes every day to re-process mostly unchanged data

**The Solution: Incremental Models**

Only process NEW or CHANGED data:

How it works:
- First run: Process ALL historical data (slow but one-time)
- Subsequent runs: Only process rows with loaded_at timestamp newer than what's already in the table
- For matching rows (same unique key): UPDATE existing row
- For new rows: INSERT

Performance impact:
- Day 1: Process 4 million rows (10 minutes)
- Day 2+: Process 50,000 new rows (30 seconds)
- 95% time savings

**Challenge 2: Query Performance on Large Tables**

**The Problem:**
When fact tables grow to millions of rows, queries slow down:
- "Show me revenue for last 30 days" scans entire table
- As table grows to 10M+ rows, queries take minutes

**The Solution: Table Partitioning (Clustering)**

Snowflake optimization - organize data by commonly queried columns:

Cluster table by date and app_id:
- When query asks for "last 30 days", Snowflake only scans those 30 days
- Doesn't touch older partitions
- 10-100x faster queries

Example query performance:
- Without clustering: Scan 5 million rows to find 50,000 matching rows (slow)
- With clustering: Scan only 50,000 rows in relevant partitions (fast)

**Challenge 3: Controlling dbt Run Times**

**The Problem:**
As models grow, running all dbt models on every run takes too long

**The Solution: Selective Model Runs**

Run only what changed:
- `dbt run --select stg_admob_revenue+` (run this model and everything downstream)
- `dbt run --select +mart_app_performance` (run this model and everything upstream)
- `dbt run --select staging.*` (run only staging layer)

For production scheduled runs:
- Staging models: Run every hour (small, fast)
- Intermediate models: Run every 6 hours
- Marts: Run once per day (expensive aggregations)

---

## Data Transformation Layers

The data flows through four distinct layers, each with a specific purpose. Think of it like a restaurant kitchen.

### Layer 1: Raw Layer (The Ingredients)

**Purpose:** Store API responses EXACTLY as received, with zero modifications.

**Why it exists:**
- Audit trail: If something breaks later, you have the original data
- Reprocessability: Can re-run transformations without calling APIs again
- Debugging: Compare transformed data to original source

**What it contains:**
- AdMob API responses dumped as-is
- Adjust API responses dumped as-is
- Metadata: When loaded, from which API call, source file name

**Example structure:**
Table: `raw.admob_network_report`
- Every column from API response (even ones you don't use)
- Additional columns: `loaded_at`, `source_file`, `api_version`

Table: `raw.adjust_deliverables`
- Every column from Adjust API
- Additional columns: `loaded_at`, `endpoint_name`

**Key principle:** NEVER delete from raw layer. This is your source of truth.

---

### Layer 2: Staging Layer (The Prep Station)

**Purpose:** Clean, standardize, and validate raw data. Make it consistent and usable.

**Analogy:** Washing vegetables, trimming meat, portioning ingredients.

**What happens here:**

**Data Cleaning:**
- Remove whitespace from text fields
- Standardize NULL handling (empty string → NULL)
- Filter out test data or invalid rows
- Remove duplicates based on unique keys

**Data Standardization:**
- Column renaming: `ESTIMATED_EARNINGS` → `revenue` (simpler, consistent)
- Consistent casing: Country codes always uppercase ("AE" not "ae")
- Platform standardization: "Android" not "android" (capitalize first letter)
- Date type conversion: String "2025-01-01" → DATE type

**Data Type Casting:**
- Revenue: String → DECIMAL(10,2)
- Dates: String → DATE
- Integers: String → INTEGER
- Explicit NULL handling (what does NULL mean for each field?)

**Example Staging Model: AdMob Revenue**

Input (raw):
- Columns named in ALL CAPS
- Revenue as string "12.34"
- Platform as lowercase "android"
- Duplicate rows possible

Output (staging):
- Columns renamed to snake_case
- Revenue as DECIMAL type
- Platform standardized to "Android"
- Duplicates removed based on (app_id, date, country, platform, hour, ad_unit)
- Added data quality flags

**Example Staging Model: Adjust Metrics**

Input (raw):
- Column named "day" (confusing)
- Column named "store_id" (not consistent with AdMob's "app_id")
- Platform as "android" (lowercase)

Output (staging):
- Renamed "day" → "date" (clear)
- Renamed "store_id" → "app_id" (consistent with AdMob)
- Platform standardized to "Android" (matches AdMob)
- Country codes uppercase (matches AdMob)

**Why this matters:**
Now AdMob and Adjust data use the same column names, same data types, same value formats. They can be joined easily in next layer.

**Validation Tests Added:**
- Revenue cannot be NULL
- Revenue must be >= 0
- Date must be within last 365 days (catch data errors)
- App_id must exist in app catalog
- Country code must be valid ISO code

---

### Layer 3: Intermediate Layer (The Cooking Station)

**Purpose:** Combine data sources, apply business logic, calculate derived metrics. NOT aggregated yet.

**Analogy:** Combining ingredients, applying cooking techniques, creating components of final dish.

**What happens here:**

**Data Integration:**
Join AdMob and Adjust data:
- Same app, same date, same country, same platform
- Combines revenue data (AdMob) with user acquisition data (Adjust)

**Business Calculations:**
Add calculated fields that business users need:

Revenue efficiency metrics:
- RPM (Revenue Per Mille) = revenue / impressions × 1000
- eCPM already from AdMob
- Revenue per user = revenue / DAU

User acquisition metrics:
- Cost Per Install = marketing_cost / installs
- Revenue per install = revenue / installs
- Immediate ROI = (revenue - marketing_cost) / marketing_cost

Quality indicators:
- Revenue discrepancy = admob_revenue - adjust_revenue (should be small)
- Engagement ratio = DAU / installs (retention proxy)

**Data Enrichment:**
Add contextual information:
- App categorization (AI apps, gaming apps, utility apps)
- Country region mapping (AE → Middle East)
- Campaign type classification (Facebook Ads → Social Media)

**Example Intermediate Model: Unified Metrics**

This model combines AdMob revenue data with Adjust user acquisition data:

Input: stg_admob_revenue + stg_adjust_metrics

Join logic:
- Match on: app_id, date, country, platform
- Left join (keep all AdMob revenue even if Adjust data missing - organic users)

Output columns:
- All dimensions: date, app_id, country, platform, campaign
- AdMob metrics: revenue, impressions, ecpm, clicks, ad_format, ad_unit
- Adjust metrics: installs, daus, sessions, marketing_cost
- Calculated metrics:
  - rpm = revenue / impressions × 1000
  - cost_per_install = marketing_cost / installs
  - revenue_per_user = revenue / daus
  - roi = (revenue - marketing_cost) / marketing_cost
  - revenue_discrepancy = admob_revenue - adjust_revenue
  - engagement_ratio = daus / installs

**Example Intermediate Model: Cohort Retention**

This model processes Adjust cohort data to track user lifetime value:

Input: stg_adjust_cohorts

Structure:
- cohort_date (the date users installed)
- app_id, country, platform, campaign
- cohort_size (how many users in this cohort)
- Retention tracking:
  - day_0_retained_users (all of them by definition)
  - day_1_retained_users (how many came back next day)
  - day_7_retained_users
  - day_30_retained_users
- Revenue tracking:
  - day_0_revenue (first day earnings)
  - day_1_revenue (cumulative through day 1)
  - day_7_revenue (cumulative through day 7)
  - day_30_revenue (cumulative through day 30 = LTV30)
- Calculated metrics:
  - day_1_retention_rate = day_1_retained / cohort_size
  - day_7_retention_rate = day_7_retained / cohort_size
  - ltv_30day = day_30_revenue / cohort_size (average LTV per user)

**Why intermediate layer is separate:**
- Business logic defined ONCE (not repeated in every mart)
- Easy to audit calculations (if ROI looks wrong, check this layer)
- Multiple marts can reuse same intermediate models
- Changes to business logic only need updating in one place

---

### Layer 4: Mart Layer (The Plated Dish)

**Purpose:** Pre-aggregated, analytics-ready tables optimized for specific business questions. Fast query performance.

**Analogy:** Final plated dishes ready to serve to customers. Each dish designed for specific preferences.

**Key characteristic:** These are AGGREGATED (summed, averaged over time/dimensions).

**Design principle:** Each mart answers specific business questions for specific stakeholders.

**Mart 1: App Performance**

**Business question:** "Which apps are most profitable? Where should we invest?"

**Stakeholder:** Product Manager, Executive Team

**Grain:** One row per app (aggregated across all time, all countries)

**Metrics included:**
- total_revenue (sum across all time)
- total_impressions
- total_installs
- total_marketing_cost
- net_roi = revenue - marketing_cost
- roi_percentage = (revenue - cost) / cost × 100
- average_ecpm
- average_rpm
- average_dau
- revenue_trend_30days (is it growing or declining?)
- profitability_score (composite metric)

**Sample query enabled:**
"Show me the top 10 most profitable apps"
"Which app has the best ROI?"
"Which apps are losing money and should be shut down?"

**Mart 2: Country Performance**

**Business question:** "Which countries should we expand to? Where do we make most money per user?"

**Stakeholder:** Marketing Manager, Business Development

**Grain:** One row per country (aggregated across all apps, all time)

**Metrics included:**
- total_revenue
- total_installs
- average_cost_per_install
- average_ltv_30day
- ltv_cac_ratio (profitability indicator)
- active_apps_count (how many apps operate there)
- revenue_rank (1 = highest revenue country)
- market_maturity (new, growing, mature based on trends)

**Enrichment:**
- region (Middle East, Asia, Americas)
- continent
- GDP per capita (if external data available)
- Mobile penetration rate

**Sample query enabled:**
"Rank countries by profitability"
"Which new countries should we launch in?"
"Where is cost per install cheapest?"

**Mart 3: Campaign ROI**

**Business question:** "Are our marketing campaigns profitable? Which campaigns should we scale up?"

**Stakeholder:** Marketing Manager, Growth Team

**Grain:** One row per campaign per country per platform

**Metrics included:**
- total_marketing_spend
- total_installs
- cost_per_install
- day_0_revenue (immediate return)
- day_7_revenue (short-term LTV)
- day_30_revenue (medium-term LTV)
- payback_period_days (how long until campaign is profitable)
- roi_30day = (day_30_revenue - cost) / cost
- user_quality_score (retention × revenue composite)

**Sample query enabled:**
"Which campaigns have positive ROI?"
"How long does it take for campaigns to break even?"
"Should we pause Campaign X because it's losing money?"

**Mart 4: Ad Monetization**

**Business question:** "Which ad formats and placements make the most money? How should we optimize ad strategy?"

**Stakeholder:** Monetization Manager, Product Team

**Grain:** One row per ad_format + ad_unit + app

**Metrics included:**
- total_impressions
- total_revenue
- average_ecpm
- average_ctr (click-through rate)
- fill_rate (what % of ad requests get filled)
- show_rate (what % of filled ads actually display)
- revenue_per_dau (monetization per user)
- optimization_recommendation (derived: "increase frequency" or "good balance")

**Sample query enabled:**
"Which ad format has highest eCPM?"
"Should we show more rewarded videos or banners?"
"Which ad placements underperform and should be removed?"

**Why marts are fast:**
- Pre-aggregated (no need to sum millions of rows on every query)
- Smaller tables (thousands of rows instead of millions)
- Optimized for specific query patterns
- Business users query these directly (don't touch raw or staging layers)

---

## Dimensional Model Design

**Philosophy**: Start with business reality (current Google Sheet structure), then evolve architecture as needed.

### Current State: Google Sheet Structure (18 Columns)

**What's Working Today:**
```
app, store_id, day, country_code, country, os_name,
install, daus, adjust_rev, adjust_imp,
ad_impressions_total_D0, ad_revenue_total_D0,
network_cost, adjust_cost, key,
admob_rev, admob_imp, paid_impressions
```

**Key Insight**: Everything is already pre-joined at daily grain by (app, country, day). This unified structure enables:
- Quick ROAS calculation: `admob_rev / network_cost`
- Revenue reconciliation: `adjust_rev vs admob_rev`
- eCPM: `(admob_rev × 1000) / admob_imp`
- IMPDAU_D0: `ad_impressions_total_D0 / daus`
- CPI: `network_cost / install`

**Business Priority**: Preserve this unified daily view - it's what teams actually use.

### Target Architecture: Business-First Dimensional Model

**Core Principle**: Build data warehouse that mirrors current workflow, then optimize.

### Phase 1: Unified Daily Fact Table (MVP for Test + Production)

**Fact Table: `fct_daily_performance`**

**Grain**: One row per app, per date, per country (matches current Google Sheet exactly)

**Purpose**: Single source of truth for all Day 0 business metrics - ROAS, eCPM, IMPDAU, CPI

**Dimensions (Foreign Keys)**:
- `date_key` → `dim_date` (calendar attributes: year, month, quarter, day_of_week)
- `app_key` → `dim_app` (app name, store_id, category, platform)
- `country_key` → `dim_country` (country name, code, region, tier)

**Adjust Metrics** (user acquisition):
- `installs` - new users today
- `daus` - daily active users
- `adjust_revenue` - estimated revenue from Adjust SDK
- `adjust_impressions` - estimated ad impressions
- `ad_impressions_d0` - actual Day 0 impressions
- `ad_revenue_d0` - actual Day 0 revenue
- `network_cost` - marketing spend
- `paid_impressions` - paid vs organic indicator

**AdMob Metrics** (source of truth revenue):
- `admob_revenue` - actual revenue (bank account reconciled)
- `admob_impressions` - actual ad impressions served

**Calculated Metrics** (dbt intermediate layer):
- `roas_d0` = `admob_revenue / NULLIF(network_cost, 0)`
- `ecpm` = `(admob_revenue × 1000) / NULLIF(admob_impressions, 0)`
- `impdau_d0` = `ad_impressions_d0 / NULLIF(daus, 0)`
- `cpi` = `network_cost / NULLIF(installs, 0)`
- `revenue_mismatch_pct` = `ABS(adjust_revenue - admob_revenue) / NULLIF(admob_revenue, 0) × 100`

**Why This Design**:
1. **Familiar**: Matches current Google Sheet exactly - zero learning curve
2. **Complete**: All ROAS calculations possible in single table query
3. **Test-Ready**: Demonstrates dimensional modeling (fact + 3 dimensions) for mid-course test
4. **Production-Ready**: Enables all business decisions documented in "How This System Enables Better Decisions"
5. **Scalable**: Can add more dimensions later (campaign, ad_format) without breaking existing queries

### Supporting Dimension Tables

**`dim_date`** (Type 1 SCD - static calendar):
- `date_key` (PK, surrogate key)
- `date` (natural key: 2025-10-22)
- `year`, `quarter`, `month`, `day`
- `day_of_week`, `day_name` (Monday, Tuesday...)
- `is_weekend` (boolean)
- `is_holiday` (optional - country-specific holidays)

**`dim_app`** (Type 1 SCD - app rarely changes):
- `app_key` (PK, surrogate key)
- `app_id` (natural key from source: `ai.video.generator.text.video`)
- `store_id` (alternate key from Adjust)
- `app_name` (display name: "AI GPT Generator")
- `category` (entertainment, productivity, utility)
- `platform` (Android, iOS)
- `launch_date`, `sunset_date` (nullable)

**`dim_country`** (Type 1 SCD - static):
- `country_key` (PK, surrogate key)
- `country_code` (natural key: TH, VN, BD)
- `country_name` (Thailand, Vietnam, Bangladesh)
- `region` (Southeast Asia, South Asia, Middle East)
- `tier` (Tier 1: US/UK/AU, Tier 2: developed, Tier 3: emerging)
- `currency` (THB, VND, BDT)

### Core Concept: Facts vs Dimensions

**Facts** = What you measure (revenue, installs, ROAS)
**Dimensions** = Context for analysis (which app, which country, when)

**Why Separate?**
- Store "Thailand" once in `dim_country`, not repeated 1M times in fact table
- Change country name in ONE place, updates everywhere
- Small dimension tables (100s of rows) join efficiently to large fact tables (millions of rows)

### Visual: Simplified Star Schema

```text
        dim_date                dim_country
            │                        │
            │                        │
            └────────┐      ┌────────┘
                     │      │
         dim_app ────┤ FACT ├──────────
                     │ TABLE│
                     └──────┘
         fct_daily_performance
```

**Why Simple**:
- No platform dimension (stored as attribute in fact table - 99.9% of apps are Android-only)
- No ad_format/ad_unit dimensions yet (AdMob data aggregated daily, can add later if needed)
- No campaign dimension yet (Adjust provides network_name, but not critical for Day 0 ROAS)
- Focus: Get ROAS calculations working perfectly first

### Example Queries Enabled by This Model

**Query 1: Yesterday's ROAS by country**
```sql
SELECT
  c.country_name,
  SUM(f.admob_revenue) as revenue,
  SUM(f.network_cost) as cost,
  SUM(f.admob_revenue) / NULLIF(SUM(f.network_cost), 0) as roas_d0
FROM fct_daily_performance f
JOIN dim_country c ON f.country_key = c.country_key
JOIN dim_date d ON f.date_key = d.date_key
WHERE d.date = CURRENT_DATE - 1
GROUP BY c.country_name
ORDER BY roas_d0 DESC;
```

**Query 2: Revenue mismatch alert**
```sql
SELECT
  a.app_name,
  c.country_name,
  d.date,
  f.adjust_revenue,
  f.admob_revenue,
  f.revenue_mismatch_pct
FROM fct_daily_performance f
JOIN dim_app a ON f.app_key = a.app_key
JOIN dim_country c ON f.country_key = c.country_key
JOIN dim_date d ON f.date_key = d.date_key
WHERE f.revenue_mismatch_pct > 5.0  -- Alert threshold
  AND d.date >= CURRENT_DATE - 7
ORDER BY f.revenue_mismatch_pct DESC;
```

**Query 3: Weekly UA team dashboard**
```sql
SELECT
  a.app_name,
  c.country_name,
  SUM(f.installs) as total_installs,
  SUM(f.network_cost) as total_spend,
  SUM(f.admob_revenue) as total_revenue,
  AVG(f.ecpm) as avg_ecpm,
  AVG(f.impdau_d0) as avg_engagement,
  SUM(f.admob_revenue) / NULLIF(SUM(f.network_cost), 0) as roas_d0
FROM fct_daily_performance f
JOIN dim_app a ON f.app_key = a.app_key
JOIN dim_country c ON f.country_key = c.country_key
JOIN dim_date d ON f.date_key = d.date_key
WHERE d.date >= CURRENT_DATE - 7
GROUP BY a.app_name, c.country_name
HAVING SUM(f.network_cost) > 100  -- Only active campaigns
ORDER BY roas_d0 ASC;  -- Worst performing first
```

### Phase 2 Considerations (Future Enhancements)

**When to Add More Dimensions**:

**Campaign Dimension** - Add when:
- Tracking >10 simultaneous campaigns
- Need campaign-level budget allocation
- A/B testing different creatives
- Columns: campaign_id, campaign_name, network, creative_type, start_date, end_date

**Ad Format/Unit Dimension** - Add when:
- Monetization optimization becomes priority
- Need to compare banner vs rewarded video performance
- AdMob API data granularity increases to include format breakdown
- Columns: ad_format (banner, interstitial, rewarded), ad_unit_id, placement_name

**Hourly Fact Table** - Add when:
- Real-time monitoring required (hourly bidding decisions)
- Peak hour analysis for optimization
- Current daily grain sufficient for ROAS optimization

**Cohort Retention Table** - Add when:
- LTV analysis needed (beyond Day 0 ROAS)
- Retention becomes key metric
- Product team needs retention data for feature validation

## Data Transformation Workflow

### Overview: From API to Analytics

**Current Manual Process** (Google Sheets):
1. Export daily data from AdMob dashboard → CSV
2. Export daily data from Adjust dashboard → CSV
3. Manual copy-paste into Google Sheet
4. VLOOKUP to match AdMob + Adjust by (app, day, country)
5. Manual formula copy-down for ROAS calculations
6. Looker Studio connects to sheet for visualization

**Target Automated Process** (Data Warehouse):
1. **Python scripts** fetch from AdMob/Adjust APIs daily
2. **Raw layer** stores exact API responses in PostgreSQL/Snowflake
3. **dbt staging** cleans and standardizes both sources
4. **dbt intermediate** joins AdMob + Adjust, calculates ROAS metrics
5. **dbt mart** creates `fct_daily_performance` with all dimensions
6. **Looker Studio** (or internal dashboard) queries Snowflake directly

### dbt Transformation Layers (3-Layer Architecture)

**Layer 1: Staging** (`models/staging/`)

Purpose: Clean and standardize raw data from each source

Models:
- `stg_admob__daily_performance` - AdMob revenue data (daily grain)
  - Convert date string `20251024` → DATE type
  - Divide microsValues by 1,000,000 for `estimated_earnings`, `observed_ecpm`
  - Cast string integers to INTEGER type
- `stg_adjust__daily_metrics` - Adjust user acquisition data (daily grain)
  - Column renaming: `store_id` → `app_id`, `day` → `date`
- Standardization: Country codes uppercase, nulls handled consistently
- Deduplication: Remove duplicates based on natural keys

**Layer 2: Intermediate** (`models/intermediate/`)

Purpose: Join sources and calculate business metrics

Models:
- `int_daily_unified` - Joins AdMob + Adjust by (app, date, country)
  - Calculates: `roas_d0`, `ecpm`, `impdau_d0`, `cpi`, `revenue_mismatch_pct`
  - Left join (keep all AdMob revenue even if Adjust missing - organic users exist)
  - Business logic centralized here (calculated once, reused everywhere)

**Layer 3: Mart** (`models/marts/`)

Purpose: Analytics-ready tables with dimensional model

Models:
- `fct_daily_performance` - Main fact table with all metrics and foreign keys
- `dim_date` - Calendar table with date attributes
- `dim_app` - App master list with metadata
- `dim_country` - Country reference with region grouping

### dbt Testing Strategy

**Required Tests** (for mid-course test points):
- **Uniqueness**: Primary keys must be unique
- **Not Null**: Critical columns cannot be null
- **Relationships**: Foreign keys must exist in dimension tables
- **Accepted Values**: Enum columns restricted to valid values
- **Custom Tests**: Business logic validation (e.g., ROAS > 0 when cost > 0)

Example `fct_daily_performance` tests:
```yaml
tests:
  - unique:
      column_name: "date_key || '-' || app_key || '-' || country_key"
  - not_null:
      column_name: date_key
  - relationships:
      to: ref('dim_app')
      field: app_key
```

---

---

## Execution Timeline

**5-Week Plan to Production-Ready Data Warehouse**

### Week 1: Foundation & Validation (Oct 19-25)

**Days 1-2: API Capability Exploration**

Goal: Confirm what data we can actually get

Tasks:
- Modify existing `api_client.py` to test different dimension combinations
- Test AdMob API with HOUR dimension for real-time capability
- Test AdMob API with AD_UNIT and FORMAT dimensions together
- Test Adjust cohort endpoints for D0, D1, D7, D30 data
- Test Adjust session metrics availability
- Document API rate limits and restrictions
- Calculate actual API call volume needed for 10 apps

Deliverable: API Capabilities Report documenting:
- ✅ What dimensions/metrics ARE available
- ❌ What's NOT available
- ⚠️ Any API limitations or constraints
- 📊 Estimated API calls needed per hour/day

**Days 3-4: Data Quality Deep Dive**

Goal: Understand data quality and identify issues before building pipeline

Tasks:
- Fetch last 7 days of AdMob data
- Fetch last 7 days of Adjust data
- Run automated quality checks:
  - Missing date gaps
  - Duplicate rows detection
  - AdMob vs Adjust revenue reconciliation
  - NULL value analysis
  - Business logic validation (negative revenue? impossible values?)
- Calculate actual data volumes per day
- Project storage requirements for 90 days

Deliverable: Data Quality Report with:
- List of discovered issues and severity ratings
- Data volume calculations (rows per day, storage needed)
- Recommended cleaning strategies
- Decision: Is data quality acceptable for business use?

**Day 5: Architecture Finalization**

Goal: Make final design decisions based on validation results

Tasks:
- Finalize which metrics to collect (based on what's available)
- Finalize data model (grain decisions based on actual data)
- Create detailed ERD diagram
- Design dbt project folder structure
- Document transformation layer responsibilities
- Plan dimension table sources

Deliverable:
- Final ERD diagram
- dbt project structure plan
- Documented design decisions and rationale

---

### Week 2: Infrastructure & Initial Load (Oct 26-Nov 1)

**Days 1-2: Database Infrastructure Setup**

Goal: Get databases running and ready for data

Tasks:
- Spin up PostgreSQL using Docker
- Create database schemas (operational, archive)
- Configure Snowflake account
- Create Snowflake schemas: RAW, STAGING, INTERMEDIATE, MART
- Set up dbt project structure
- Configure profiles.yml for PostgreSQL and Snowflake connections
- Test connections from dbt to both databases

Deliverable:
- Running PostgreSQL instance
- Configured Snowflake environment
- Initialized dbt project with working connections

**Days 3-5: Historical Data Collection**

Goal: Load 90 days of historical data into Snowflake

Tasks:
- Build Python ingestion scripts:
  - `pipelines/collect_admob_historical.py` - Fetch 90 days from AdMob API
  - `pipelines/collect_adjust_historical.py` - Fetch 90 days from Adjust API
  - `pipelines/load_to_snowflake.py` - Bulk load CSVs to Snowflake RAW schema
- Handle API pagination for large date ranges
- Implement error handling and retry logic
- Add progress logging
- Execute historical load
- Validate row counts and data integrity

Deliverable:
- 90 days of historical data in Snowflake RAW schema
- Ingestion scripts ready for daily incremental runs
- Validation report confirming data loaded correctly

---

### Week 3: Data Transformation Foundation (Nov 2-8)

**Days 1-2: Staging Layer**

Goal: Clean and standardize raw data

Tasks:
- Build `models/staging/stg_admob_revenue.sql`
  - Column renaming and type casting
  - Deduplication logic
  - NULL handling
  - Date validation
- Build `models/staging/stg_adjust_metrics.sql`
  - Standardize column names to match AdMob
  - Platform and country code normalization
  - Type casting
- Add `schema.yml` files with dbt tests:
  - not_null tests on critical fields
  - unique tests on composite keys
  - accepted_range tests on numeric fields
  - recency tests for data freshness
- Run `dbt run` and `dbt test`
- Fix any test failures

Deliverable:
- Working staging models passing all tests
- Documented staging layer schema

**Days 3-4: Intermediate Layer**

Goal: Combine data sources and add business calculations

Tasks:
- Build dimension seed files:
  - `seeds/dim_app.csv` - Master app list
  - `seeds/dim_country.csv` - Country reference
  - `seeds/dim_platform.csv` - Platform reference
  - Load with `dbt seed`
- Build `models/intermediate/int_unified_metrics.sql`
  - Join AdMob and Adjust staging tables
  - Add calculated fields (ROI, CPI, RPM, etc.)
  - Revenue discrepancy calculation
- Build `models/intermediate/int_cohort_retention.sql` (if cohort data available)
  - Pivot cohort maturity days
  - Calculate retention rates
  - Calculate cumulative LTV
- Add tests for calculation logic
- Run and validate

Deliverable:
- Dimension tables loaded
- Intermediate models combining data sources
- Business calculations validated

**Day 5: Dimension Models**

Goal: Build analytical dimensions

Tasks:
- Build `models/dimensions/dim_app.sql` (enrich from seed)
  - Add app categorization logic
  - Add status flags
- Build `models/dimensions/dim_country.sql` (enrich from seed)
  - Add regional groupings
- Build `models/dimensions/dim_date.sql`
  - Generate calendar for 2024-2026
  - Add all date attributes (week, month, quarter, etc.)
- Build `models/dimensions/dim_ad_format.sql`
- Build `models/dimensions/dim_ad_unit.sql`
- Run and validate

Deliverable:
- Complete dimension tables ready for fact table joins

---

### Week 4: Fact Tables & Marts (Nov 9-15)

**Days 1-2: Fact Tables**

Goal: Build star schema fact tables

Tasks:
- Build `models/marts/fact_revenue_daily.sql`
  - Join intermediate model with all dimensions
  - Generate surrogate keys
  - Configure as incremental model
  - Add partitioning/clustering hints
- Build `models/marts/fact_cohort_retention.sql` (if applicable)
  - Cohort-based fact table
  - Configure incremental logic
- Test incremental behavior:
  - Full refresh first run
  - Incremental run with new data
  - Validate deduplication works
- Add comprehensive tests

Deliverable:
- Working fact tables with incremental logic
- Validated star schema relationships

**Days 3-4: Analytics Marts**

Goal: Build pre-aggregated business marts

Tasks:
- Build `models/marts/mart_app_performance.sql`
  - App-level aggregations
  - ROI calculations
  - Trend indicators
- Build `models/marts/mart_country_performance.sql`
  - Geographic aggregations
  - Market rankings
- Build `models/marts/mart_campaign_roi.sql`
  - Campaign attribution
  - LTV calculations
  - Payback period
- Build `models/marts/mart_ad_monetization.sql`
  - Ad format comparisons
  - Ad unit rankings
- Run full dbt pipeline: `dbt build`
- Validate all tests pass

Deliverable:
- Complete set of analytics marts
- Validated business calculations
- Documented mart purposes and usage

**Day 5: Real-Time Pipeline**

Goal: Set up hourly data collection to PostgreSQL

Tasks:
- Build `pipelines/collect_realtime_admob.py`
  - Fetch hourly data for today
  - Load to PostgreSQL operational schema
  - Upsert logic (update if exists)
- Build `pipelines/archive_to_snowflake.py`
  - Move data older than 30 days from PostgreSQL to Snowflake
  - Delete from PostgreSQL after successful archive
- Test manual execution
- Set up cron job or scheduler for hourly runs
- Validate real-time updates work

Deliverable:
- Working real-time pipeline to PostgreSQL
- Automated archival process
- Scheduled execution configured

---

### Week 5: Testing, Documentation & Polish (Nov 16-22)

**Days 1-2: End-to-End Testing**

Goal: Validate complete system works

Tasks:
- Run complete dbt build from scratch
- Test incremental refresh with new day's data
- Validate data lineage (raw → staging → intermediate → mart)
- Performance testing:
  - Query response times on marts
  - dbt run times
  - Incremental vs full refresh times
- Create sample analytical queries:
  - "Top 10 profitable apps"
  - "Country expansion recommendations"
  - "Campaign ROI by country"
  - "Best performing ad formats"
- Verify query results make business sense

Deliverable:
- Validated end-to-end pipeline
- Sample query library
- Performance benchmarks

**Days 3-4: Documentation**

Goal: Document everything for handoff

Tasks:
- Create data dictionary:
  - Every table documented
  - Every column explained with business meaning
  - Example queries for each mart
- Update ERD with final schema
- Write user guide for business team:
  - How to query marts
  - What questions each mart answers
  - Metric definitions (what is LTV? ROI? etc.)
- Document dbt models:
  - Add descriptions to all models
  - Document calculation logic
  - Add column descriptions
- Create dbt docs site: `dbt docs generate && dbt docs serve`

Deliverable:
- Complete documentation package
- Business user guide
- dbt documentation site

**Day 5: Mid-Course Test Preparation**

Goal: Ensure all test requirements met

Tasks:
- Verify test checklist:
  - ✅ 2+ data sources (AdMob + Adjust)
  - ✅ Real-time pipeline (PostgreSQL hourly)
  - ✅ Batch pipeline (Snowflake historical)
  - ✅ Docker (PostgreSQL container)
  - ✅ dbt transformations (4 layers)
  - ✅ Dimensional model (facts + dimensions)
  - ✅ Incremental models
  - ✅ dbt tests
  - ✅ Custom macro (create during dbt work)
  - ✅ Git workflow (feature branches + PRs)
  - ✅ ERD diagram
- Create demo presentation
- Prepare to explain architecture and design decisions
- Final git commit and push

Deliverable:
- Test-ready data warehouse
- Demo materials
- Complete documentation

---

## Success Metrics

### Mid-Course Test Requirements (Pass: 50 pts, Target: 70+ pts)

**Data Ingestion (35 pts):**
- ✅ Git workflow with feature branches and PRs (evidence in git history)
- ✅ Python ingestion scripts for both sources (working code in repo)
- ✅ Docker PostgreSQL setup (docker-compose.yml, working container)
- ✅ Real-time and batch pipelines documented and functional

**Transformation (40 pts):**
- ✅ Multi-layer dbt models (staging, intermediate, mart)
- ✅ Incremental models (configured and tested)
- ✅ Custom dbt macro (created and used)
- ✅ dbt tests on models (passing tests)
- ✅ ERD diagram showing dimensional model
- ✅ Documented business logic

**CI/CD (5 pts):**
- ✅ GitHub Actions workflow (basic - can add later if time)

**Extra Features (20 pts - target at least 10):**
- ✅ Advanced dimensional modeling (star schema with 5+ dimensions)
- ✅ Data quality validation framework (comprehensive dbt tests)
- ✅ Real-time monitoring capability (PostgreSQL operational database)
- ✅ Cohort retention analysis (if time permits)

**Expected Score:** 75-80 points (well above passing)

### Business Value Metrics

**Operational Efficiency:**
- Query response time < 3 seconds for all mart queries
- Daily pipeline execution < 10 minutes (incremental)
- Real-time updates within 2 hours of actual events

**Data Quality:**
- Revenue reconciliation: AdMob vs Adjust within 5%
- Zero critical data quality test failures
- No missing dates in 90-day period

**Business Enablement:**
- Answer all current analytics team questions
- PLUS answer advanced questions they can't currently answer:
  - 30-day LTV by country and campaign
  - Ad format optimization recommendations
  - User retention cohort analysis
  - Campaign payback period calculations

**Scalability:**
- System handles current 10 apps easily
- Can scale to 50+ apps without architecture changes
- Incremental processing keeps run times manageable

### Future Enhancements (Post Mid-Course)

**Capstone Project Extensions:**
- AI agent with natural language query interface
- Real-time alerting (Slack/email when revenue drops)
- Predictive LTV modeling using historical cohorts
- Automated campaign optimization recommendations
- Interactive dashboards (Streamlit or similar)
- Advanced anomaly detection

**Production Readiness:**
- Comprehensive monitoring and logging
- Data lineage tracking
- SLA monitoring (data freshness, pipeline health)
- Automated testing in CI/CD
- Disaster recovery procedures

---

## Final Notes

**Philosophy: Build for Real Business Value**

This isn't just a school project. This is a production-grade data warehouse that will actually help your mobile app business make better decisions:

- Marketing team can see which campaigns are profitable
- Product team can identify which apps to invest in
- Executive team gets clear ROI visibility
- Operations team monitors revenue in real-time

**Validation Before Building**

We're spending Week 1 entirely on validation because building on wrong assumptions wastes weeks. Better to discover data quality issues or API limitations early.

**Incremental Complexity**

We start simple (staging layer) and add complexity gradually (intermediate, marts). Each layer builds on validated previous layers. If something breaks, we know exactly where.

**Industry Standards**

Everything in this plan reflects real-world data engineering practices:
- Star schema dimensional modeling
- Incremental processing
- Data quality testing
- Hot/cold storage architecture
- Clear layer separation

**Realistic Timeline**

5 weeks is tight but achievable for one person working efficiently. The plan assumes:
- 4-6 hours per day dedicated to this
- Some problem-solving time built in
- Focus on core requirements first, enhancements later

**Success Definition**

Success = Pass mid-course test (70+ pts) AND deliver real business value to your mobile app company. If the analytics team actually uses this warehouse, you've succeeded beyond the test.

---

## Revision Summary (Oct 19, 2025)

✅ **API Validation Complete** - Updated with actual tested capabilities

**Key Changes:**
1. **Architecture:** Real-time hourly pipeline confirmed viable (Adjust API)
2. **Data Volumes:** Updated with actual test results (13.5K AdMob rows/day, 936 Adjust hourly rows/day)
3. **Dimensional Model:** Added `fact_acquisition_hourly` for real-time PostgreSQL pipeline
4. **Fact Tables:** 4 tables total (1 hourly real-time + 3 daily historical)
5. **Limitations:** HOUR dimension NOT available in AdMob, IAP revenue NOT tracked

**What Changed:**
- Original plan: Assumed hourly for both sources
- Validated reality: Hourly only from Adjust, daily from AdMob
- Architecture impact: PostgreSQL for Adjust hourly + Snowflake for both daily

**What Stayed:**
- Hot/cold storage strategy
- Star schema dimensional modeling
- 3-layer dbt transformation (staging → intermediate → mart)
- Business metrics focus (LTV, CAC, ROI, retention)

**Ready For:** Implementation Phase

---

**Last Updated:** October 19, 2025 (Revised with API validation results)
**Status:** ✅ Planning Complete - Ready for Implementation
**Next Action:** Design dbt project structure and begin staging models
