# Mobile Analytics Data Strategy - Complete Planning Document

**Project Goal:** Build a production-grade data warehouse that delivers real business value to mobile app publishers while passing mid-course test requirements.

**Success Criteria:**
- Pass mid-course test (70+ points)
- Provide actionable insights for mobile app business decisions
- Handle real-world data volumes efficiently
- Industry-standard architecture and practices

---

## Table of Contents

1. [Business Problem & Value](#business-problem--value)
2. [Data Architecture Overview](#data-architecture-overview)
3. [Data Sources & Metrics](#data-sources--metrics)
4. [Validation Roadmap](#validation-roadmap)
5. [Data Transformation Layers](#data-transformation-layers)
6. [Dimensional Model Design](#dimensional-model-design)
7. [Execution Timeline](#execution-timeline)
8. [Success Metrics](#success-metrics)

---

## Business Problem & Value

### The Real-World Business Context

You run a mobile app publishing company with multiple apps generating revenue through in-app advertising. Every day, critical business decisions need answers:

**Daily Operations:**
- "How much money did we make yesterday?"
- "Which app is performing best right now?"
- "Should we pause this marketing campaign because it's losing money?"

**Strategic Planning:**
- "Which country should we expand to next?"
- "What's the return on investment for our marketing spend?"
- "Should we invest more in App A or shut it down?"

**Current Pain Points:**
- Data scattered across CSV exports from different platforms
- Manual analysis in spreadsheets (slow, error-prone)
- No real-time visibility into revenue changes
- Can't easily calculate user lifetime value or retention
- Marketing team can't see if campaigns are profitable

### The Core Business Metrics

Understanding mobile app profitability requires tracking the complete user journey:

**User Acquisition (The Cost Side):**
- You spend money on ads to get users to install your app
- **Cost Per Install (CPI)** = Marketing spend divided by number of installs
- Different countries and campaigns have different costs

**Monetization (The Revenue Side):**
- Users see ads in your app, generating revenue
- **Day 0 Revenue** = Money made on install day
- **Lifetime Value (LTV)** = Total money a user generates over weeks/months
- Revenue depends on user retention (do they come back?)

**The Profitability Equation:**
```
Profit Per User = Lifetime Value - Cost Per Install

If LTV > CPI → Profitable, scale up marketing!
If LTV < CPI → Losing money, fix monetization or stop marketing
```

**The Critical Ratio: LTV:CAC (Lifetime Value to Customer Acquisition Cost)**
- Greater than 3:1 → Healthy business, invest more
- Between 1:1 and 3:1 → Profitable but tight margins
- Less than 1:1 → Losing money on every user

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
- Long-term profitability (Lifetime Value beyond day 0)
- Retention cohort analysis (Day 7, Day 30 retention rates)
- Ad format optimization (which ad types make most money)
- Session depth and user engagement patterns
- Sophisticated user segmentation

---

## Data Architecture Overview

### Industry Standard: Hot vs Cold Storage

Real companies don't keep all data in one database. They use a two-tier architecture:

**Hot Storage (PostgreSQL) - Operational Database**
- **Purpose:** Fast access to recent data for operational decisions
- **Data Retained:** Last 30 days of detailed data
- **Update Frequency:** Every hour (real-time pipeline)
- **Use Case:** "What's happening RIGHT NOW?"
- **Who Uses It:** Operations team, real-time dashboards, alerting systems
- **Cost:** Expensive (fast databases cost more)

**Cold Storage (Snowflake) - Analytical Warehouse**
- **Purpose:** All historical data for strategic analysis
- **Data Retained:** Forever (all historical data)
- **Update Frequency:** Once daily (batch pipeline)
- **Use Case:** "What patterns exist over 6 months?"
- **Who Uses It:** Analytics team, business intelligence, strategic planning
- **Cost:** Cheap (columnar storage, compressed)

**The Key Insight:** You never delete data. You move it from hot to cold storage.

### Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA SOURCES                              │
├─────────────────────────────────────────────────────────────┤
│  AdMob API                    │  Adjust API                  │
│  - Revenue & Impressions      │  - User Acquisition          │
│  - Ad Performance             │  - Retention Cohorts         │
│  - Hourly + Daily Data        │  - Marketing Costs           │
└──────────────┬────────────────┴──────────────┬───────────────┘
               │                                │
               │                                │
    ┌──────────▼──────────┐          ┌─────────▼──────────┐
    │  REAL-TIME PIPELINE │          │  BATCH PIPELINE     │
    │  (Every Hour)       │          │  (Daily)            │
    └──────────┬──────────┘          └─────────┬──────────┘
               │                                │
               │                                │
    ┌──────────▼──────────┐          ┌─────────▼──────────┐
    │   PostgreSQL        │          │   Snowflake         │
    │   (Last 30 days)    │──Archive→│   (All History)     │
    │   Fast queries      │  Daily   │   Deep analytics    │
    └──────────┬──────────┘          └─────────┬──────────┘
               │                                │
               │                                │
               └────────────┬───────────────────┘
                            │
                   ┌────────▼────────┐
                   │   dbt Transform  │
                   │   Raw → Staging  │
                   │   → Intermediate │
                   │   → Mart         │
                   └────────┬────────┘
                            │
               ┌────────────┴────────────┐
               │                         │
    ┌──────────▼──────────┐   ┌─────────▼──────────┐
    │  Business Dashboards│   │  AI Agent (Future) │
    │  Operational Alerts │   │  Natural Language  │
    │  Executive Reports  │   │  Query Interface   │
    └─────────────────────┘   └────────────────────┘
```

### Why This Architecture?

**Real-Time Pipeline (PostgreSQL):**
- Marketing manager sees campaign spending too much → pause it NOW
- Revenue drops 50% in last hour → investigate server issues
- New app launched → monitor performance in real-time

**Batch Pipeline (Snowflake):**
- CFO asks "What was our revenue growth last quarter?"
- Product team analyzes "Which countries have best 30-day retention?"
- Data scientist builds LTV prediction model using 6 months of cohort data

**Archive Process:**
- Every night, data older than 30 days moves from PostgreSQL to Snowflake
- PostgreSQL stays fast (less data)
- Snowflake stores everything (cheap storage)
- Nothing is ever deleted

---

## Data Sources & Metrics

### AdMob API - Revenue & Monetization Data

AdMob provides detailed ad performance data showing how your apps make money.

**Dimensions (How to Slice the Data):**

*Time Dimensions:*
- **DATE** - Daily breakdown
- **HOUR** - Hourly breakdown (for real-time tracking)
- **WEEK, MONTH** - Aggregated views

*App Dimensions:*
- **APP** - Which application
- **AD_UNIT** - Specific ad placement within app (e.g., "home_screen_banner", "game_over_interstitial")
- **FORMAT** - Ad type (banner, interstitial, rewarded video, native, app open)

*Geographic & Platform:*
- **COUNTRY** - User location
- **PLATFORM** - iOS or Android

*Monetization Network:*
- **AD_SOURCE** - Which ad network filled the ad (AdMob Network, Meta Audience Network, Unity Ads, etc.)

**Metrics (What to Measure):**

*Revenue Metrics:*
- **ESTIMATED_EARNINGS** - Actual money made (the main metric)
- **OBSERVED_ECPM** - Effective cost per 1000 impressions (revenue efficiency indicator)

*Volume Metrics:*
- **IMPRESSIONS** - How many ads were shown
- **CLICKS** - How many ads were clicked
- **AD_REQUESTS** - How many times app asked for an ad

*Performance Metrics:*
- **MATCHED_REQUESTS** - How many ad requests got filled with an ad
- **MATCH_RATE** - Percentage of requests that got filled (inventory health)
- **SHOW_RATE** - Percentage of matched ads actually displayed (technical health)
- **CLICK_THROUGH_RATE** - Percentage of impressions that got clicked

**Business Value of Each Metric:**

- **ESTIMATED_EARNINGS:** The money. Self-explanatory.
- **OBSERVED_ECPM:** Which ad format or placement makes most money per impression? Should you show more rewarded videos (high eCPM) or banners (high volume)?
- **MATCH_RATE:** Are ad networks able to fill your requests? Low match rate means lost revenue opportunity.
- **SHOW_RATE:** Are ads loading correctly? Low show rate indicates technical issues.
- **AD_UNIT performance:** Which placements in your app monetize best? Home screen? After level completion?

### Adjust API - User Acquisition & Behavior Data

Adjust tracks user acquisition, engagement, and attribution (which marketing campaign brought each user).

**Dimensions:**

*Time & App:*
- **day** - Date
- **app, store_id** - Application identifier
- **country_code, os_name** - Geographic and platform

*Marketing Attribution:*
- **tracker_name** - Marketing campaign name
- **creative_name** - Which ad creative (image/video) was shown
- **network** - Ad platform (Facebook Ads, Google Ads, TikTok Ads, etc.)

*Cohort Analysis:*
- **cohort_maturity** - Days since install (D0, D1, D7, D30)

**Metrics:**

*Acquisition Metrics:*
- **installs** - New users acquired
- **network_cost** - Money spent on marketing
- **clicks, impressions** - Marketing ad performance

*Engagement Metrics:*
- **daus** - Daily Active Users (how many opened app today)
- **sessions** - Total app opens
- **session_length** - How long users stay in app

*Retention Metrics (Cohort-Based):*
- **retained_users** - How many users from install cohort came back on Day 1, 7, 30
- **retention_rate** - Percentage of cohort still active
- **events** - Custom in-app actions (level completed, purchase made, etc.)

*Revenue Metrics:*
- **ad_revenue** - Should match AdMob data (validation check)
- **ad_impressions** - Should match AdMob
- **iap_revenue** - In-app purchase revenue (if applicable)

**Business Value:**

- **Cost Per Install (CPI):** network_cost divided by installs - tells you if Country A is cheaper to acquire users than Country B
- **User Quality:** Do expensive users (high CPI) actually generate more revenue? Or are cheap users better?
- **Retention Rates:** If only 10% of users come back on Day 7, you have a retention problem
- **Lifetime Value:** Track same cohort over 30 days to see total revenue per user
- **Campaign Attribution:** Which marketing campaign brings highest-quality users?

### Data Volume Estimates

**AdMob API Volume Calculation:**

Assuming you have:
- 10 active apps
- Average 15 countries per app (some apps global, some regional)
- 2 platforms (iOS, Android)
- 24 hours per day (for real-time)
- 5 ad formats
- 3 ad units per app on average

Theoretical maximum rows per day:
`10 apps × 15 countries × 2 platforms × 24 hours × 5 formats × 3 ad units = 108,000 rows/day`

**Reality check:** Not all combinations exist:
- Some apps not launched in all countries
- Some ad formats not used in all apps
- Many hours have zero impressions (especially overnight)

**Realistic estimate:** 20,000 to 40,000 rows per day

Over 90 days historical load: **1.8 to 3.6 million rows**

**Adjust API Volume Calculation:**

Simpler structure (no hourly breakdown, no ad unit dimension):
- 10 apps × 15 countries × 2 platforms = 300 rows per day (deliverables endpoint)

Cohort data (each install cohort tracked for 30 days):
- 300 install combinations per day × 30 cohort maturity days = 9,000 cohort rows per day

**Total Adjust:** Approximately 10,000 rows per day

Over 90 days: **900,000 rows**

**Combined Total Data Volume:**
- **90-day historical load:** 4 to 5 million rows
- **Daily incremental:** 50,000 new rows per day
- **Storage estimate:** 2-3 GB raw CSV, 500 MB in Snowflake (compressed), 200 MB in PostgreSQL (30 days)

**Is This Manageable?**
Yes. This is considered SMALL by industry standards. Snowflake and PostgreSQL handle millions of rows easily. Query performance will be excellent with proper indexing and partitioning.

---

## Validation Roadmap

Before building anything, we must validate assumptions. Shit hits the fan when you build for data you can't actually get.

### Phase 0: "Can We Actually Get The Fucking Data?"

**Critical Questions to Answer:**

1. Are the dimensions and metrics we want actually available from the APIs?
2. Can we combine certain dimensions together, or do APIs have limitations?
3. What are the API rate limits? Will we hit them?
4. How far back can we fetch historical data?
5. Is the data quality good enough to make business decisions?

**Validation Step 1: API Capability Testing**

Test with your existing API client to verify what's actually available:

**AdMob Tests:**
- Can we fetch HOUR dimension? (Required for real-time)
- Can we request multiple dimensions together (DATE + HOUR + APP + COUNTRY + FORMAT + AD_UNIT)?
- What's the maximum date range per API call? 30 days? 90 days?
- Do all metrics work with all dimension combinations?
- Are there undocumented restrictions?

**Adjust Tests:**
- Can we access cohort endpoints (retention data by D0, D1, D7, D30)?
- Can we get session-level data (session length, sessions per user)?
- Can we get campaign attribution data (tracker name, creative name)?
- Can we get revenue broken down by cohort day?
- What's the oldest data available? 90 days? 180 days?

**Rate Limit Testing:**
- How many API requests can we make per hour?
- If we have 10 apps and need hourly data, do we hit limits?
- Do we need to implement request throttling?

**Expected Outcome:**
- Document exactly which dimensions and metrics ARE available
- Document what's NOT available (so we don't plan for impossible things)
- Understand API constraints and plan around them

**Validation Step 2: Data Volume Reality Check**

Fetch one day of actual data and count the rows:

Example: Fetch yesterday's AdMob data with all dimensions:
- Actual rows returned: 35,000 rows
- Multiply by 90 days: 3.15 million rows (confirmed our estimate)

Fetch one day of Adjust data:
- Actual rows: 8,500 rows
- Multiply by 90 days: 765,000 rows (slightly less than estimate)

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

The dimensional model (star schema) is how we organize data for efficient analytics. It separates FACTS (measurements) from DIMENSIONS (context).

### Core Concept: Facts vs Dimensions

**Facts (Measurements):**
- Things you measure and want to analyze
- Numeric values that can be summed, averaged
- Examples: revenue, impressions, installs, costs
- Large tables (millions of rows)

**Dimensions (Context):**
- Descriptive attributes that give facts meaning
- Text and categorical data
- Examples: which app, which country, which date, which ad format
- Small tables (hundreds to thousands of rows)

**Why separate them?**
- Efficiency: Store "United States" once in dimension table, not repeated 1 million times in fact table
- Consistency: Change country name in ONE place (dimension), updates everywhere
- Query performance: Small dimension tables join to large fact tables efficiently

### The Star Schema Structure

Imagine a star with fact table in center, dimension tables radiating outward:

```
        dim_date              dim_country
            │                      │
            │                      │
            └─────┐          ┌─────┘
                  │          │
    dim_app ──────┤  FACT   ├────── dim_platform
                  │  TABLE  │
                  │          │
            ┌─────┘          └─────┐
            │                      │
            │                      │
     dim_ad_format            dim_campaign
```

### Fact Table 1: fact_revenue_daily

**Purpose:** Daily revenue and user metrics at the most detailed level

**Grain:** One row per app, per date, per country, per platform, per ad_format, per ad_unit

**Primary key:** revenue_id (surrogate key generated from dimension combination)

**Foreign keys (links to dimensions):**
- app_id → dim_app
- date_id → dim_date
- country_id → dim_country
- platform_id → dim_platform
- ad_format_id → dim_ad_format
- ad_unit_id → dim_ad_unit
- campaign_id → dim_campaign (nullable for organic users)

**Metrics (Measurements):**

Revenue metrics:
- revenue (from AdMob)
- impressions
- clicks
- ecpm
- rpm (calculated)

User acquisition metrics:
- installs
- marketing_cost
- cost_per_install (calculated)

Engagement metrics:
- daus
- sessions
- session_length

Calculated business metrics:
- revenue_per_user
- roi (revenue - marketing_cost)
- engagement_ratio (daus / installs)

Metadata:
- loaded_at (when row was created)
- updated_at (when row was last modified)

**Example row:**
```
revenue_id: 12345
app_id: 5 (links to "AI Video Generator" in dim_app)
date_id: 20250115 (links to January 15, 2025 in dim_date)
country_id: 10 (links to "United Arab Emirates" in dim_country)
platform_id: 1 (links to "Android" in dim_platform)
ad_format_id: 3 (links to "Rewarded Video" in dim_ad_format)
ad_unit_id: 22 (links to "game_complete_reward" in dim_ad_unit)
campaign_id: 105 (links to "Facebook_UAE_Jan" in dim_campaign)
revenue: 145.50
impressions: 3200
daus: 850
installs: 120
marketing_cost: 95.00
roi: 0.53 (53% return)
```

**Query example:**
"Show me total revenue by app for January 2025"
```sql
SELECT
  a.app_name,
  SUM(f.revenue) as total_revenue
FROM fact_revenue_daily f
JOIN dim_app a ON f.app_id = a.app_id
JOIN dim_date d ON f.date_id = d.date_id
WHERE d.year = 2025 AND d.month = 1
GROUP BY a.app_name
```

### Fact Table 2: fact_cohort_retention

**Purpose:** Track user cohorts over time to measure retention and lifetime value

**Grain:** One row per install cohort, per cohort_day (D0, D1, D7, D30)

**Primary key:** cohort_id

**Foreign keys:**
- app_id → dim_app
- cohort_date_id → dim_date (the date users installed)
- country_id → dim_country
- platform_id → dim_platform
- campaign_id → dim_campaign

**Dimensions:**
- cohort_maturity (D0, D1, D7, D30 - days since install)

**Metrics:**

Cohort size:
- cohort_size (total installs in this cohort)

Retention:
- retained_users (how many still active)
- retention_rate (retained / cohort_size)

Revenue:
- cumulative_revenue (total revenue from this cohort through cohort_day)
- revenue_per_user (cumulative_revenue / cohort_size)

Engagement:
- active_sessions
- avg_session_length

**Example row:**
```
cohort_id: 67890
app_id: 5
cohort_date_id: 20250110 (users who installed on Jan 10)
country_id: 10 (UAE)
platform_id: 1 (Android)
campaign_id: 105
cohort_maturity: "D7" (7 days after install)
cohort_size: 250 (250 users installed on Jan 10)
retained_users: 45 (45 still active on Day 7)
retention_rate: 0.18 (18% retention)
cumulative_revenue: 125.50 (total revenue from this cohort through D7)
revenue_per_user: 0.50 (LTV at D7 = $0.50 per user)
```

**Query example:**
"What's the Day 7 retention rate for users from Facebook campaigns?"
```sql
SELECT
  c.campaign_name,
  AVG(f.retention_rate) as avg_d7_retention
FROM fact_cohort_retention f
JOIN dim_campaign c ON f.campaign_id = c.campaign_id
WHERE f.cohort_maturity = 'D7'
GROUP BY c.campaign_name
```

### Dimension Table: dim_app

**Purpose:** Master list of all apps with descriptive attributes

**Grain:** One row per app

**Primary key:** app_id (surrogate key, auto-increment integer)

**Natural key:** store_id (unique app package identifier like "com.example.app")

**Attributes:**
- app_name (display name: "AI Video Generator")
- store_id (package ID: "ai.video.generator.text.video")
- category (AI Apps, Gaming, Utility)
- subcategory (Video Editing, Puzzle Games, etc.)
- launch_date (when app first released)
- status (Active, Sunset, Beta)
- primary_market (which country is main focus)
- description (what app does)

**Slowly Changing Dimension Type:** Type 1 (overwrite changes, don't track history)

Why Type 1: App name might change, but we don't need historical names. Current value is fine.

### Dimension Table: dim_country

**Purpose:** Geographic reference with regional groupings

**Grain:** One row per country

**Primary key:** country_id

**Natural key:** country_code (ISO 2-letter: "AE", "US", "IN")

**Attributes:**
- country_code ("AE")
- country_name ("United Arab Emirates")
- region ("Middle East")
- continent ("Asia")
- subregion ("Western Asia")
- currency ("AED")
- language_primary ("Arabic")

**Optional enrichment:**
- gdp_per_capita (economic indicator)
- mobile_penetration_rate (market maturity indicator)
- population
- timezone_primary

### Dimension Table: dim_date

**Purpose:** Calendar table with date attributes for time-based analysis

**Grain:** One row per date

**Primary key:** date_id (YYYYMMDD format: 20250115)

**Natural key:** date (DATE type: 2025-01-15)

**Attributes:**

Basic:
- date (2025-01-15)
- day_name (Wednesday)
- day_of_week (3)
- day_of_month (15)
- day_of_year (15)

Week:
- week_number (3)
- week_start_date (Monday of that week)
- week_end_date (Sunday of that week)

Month:
- month_number (1)
- month_name (January)
- month_abbr (Jan)
- month_start_date
- month_end_date

Quarter:
- quarter (Q1)
- quarter_start_date
- quarter_end_date

Year:
- year (2025)
- fiscal_year (if different from calendar year)

Special flags:
- is_weekend (TRUE/FALSE)
- is_holiday (TRUE/FALSE)
- is_month_end (TRUE/FALSE)
- is_quarter_end (TRUE/FALSE)

**Why this is useful:**
Makes time-based queries easy:
- "Show revenue for all weekends"
- "Compare Q1 2025 to Q1 2024"
- "Exclude holidays from analysis"

### Dimension Table: dim_platform

**Purpose:** Operating system reference

**Grain:** One row per platform

**Primary key:** platform_id

**Attributes:**
- platform_name ("Android")
- os_family ("Android")
- vendor ("Google")

Simple table (only 2-3 rows total: Android, iOS, maybe Web)

### Dimension Table: dim_ad_format

**Purpose:** Ad type reference

**Grain:** One row per ad format type

**Primary key:** ad_format_id

**Attributes:**
- format_name ("Rewarded Video")
- format_code ("rewarded_video")
- format_category ("Video Ads")
- is_interruptive (TRUE for interstitial, FALSE for banner)
- typical_ecpm_range ("$10-$20")

**Example rows:**
- Banner (small ad at top/bottom, low eCPM, high volume)
- Interstitial (full-screen ad, medium eCPM, medium volume)
- Rewarded Video (user watches for reward, high eCPM, lower volume)
- Native (blended into app content)
- App Open (shown when app launches)

### Dimension Table: dim_ad_unit

**Purpose:** Specific ad placements within apps

**Grain:** One row per ad unit (unique ad placement)

**Primary key:** ad_unit_id

**Attributes:**
- ad_unit_name ("game_complete_reward")
- ad_unit_code (technical ID from AdMob)
- app_id (which app this ad unit belongs to)
- ad_format_id (which format type)
- placement_description ("Shown after user completes level")
- is_active (TRUE/FALSE)

**Example rows for video generator app:**
- "home_banner" - Banner on home screen
- "export_interstitial" - Interstitial after video export
- "premium_reward" - Rewarded video for premium features

### Dimension Table: dim_campaign

**Purpose:** Marketing campaign tracking

**Grain:** One row per campaign

**Primary key:** campaign_id

**Attributes:**
- campaign_name ("Facebook_UAE_Video_Jan2025")
- campaign_code (internal tracking code)
- network ("Facebook Ads")
- campaign_type ("User Acquisition")
- start_date
- end_date
- budget_allocated
- target_country
- target_platform
- creative_type ("Video Ad", "Static Image", "Carousel")
- objective ("Installs", "Brand Awareness")
- is_active

**Special handling:**
- campaign_id = 0 for organic users (no paid campaign)
- Allows filtering paid vs organic easily

### Entity Relationship Diagram

```
┌─────────────────────┐
│     dim_app         │
│ ─────────────────── │
│ PK: app_id          │
│ store_id            │
│ app_name            │
│ category            │
│ launch_date         │
└──────────┬──────────┘
           │
           │ 1
           │
           │ N
┌──────────▼──────────────────────────────────────┐
│         fact_revenue_daily                      │
│ ──────────────────────────────────────────────  │
│ PK: revenue_id                                  │
│ FK: app_id ─────────────┐                       │
│ FK: date_id ────────────┼────┐                  │
│ FK: country_id ─────────┼────┼───┐              │
│ FK: platform_id ────────┼────┼───┼───┐          │
│ FK: ad_format_id ───────┼────┼───┼───┼───┐      │
│ FK: ad_unit_id ─────────┼────┼───┼───┼───┼─┐    │
│ FK: campaign_id ────────┼────┼───┼───┼───┼─┼─┐  │
│                         │    │   │   │   │ │ │  │
│ revenue                 │    │   │   │   │ │ │  │
│ impressions             │    │   │   │   │ │ │  │
│ installs                │    │   │   │   │ │ │  │
│ daus                    │    │   │   │   │ │ │  │
│ marketing_cost          │    │   │   │   │ │ │  │
│ roi                     │    │   │   │   │ │ │  │
└─────────────────────────┼────┼───┼───┼───┼─┼─┼──┘
                          │    │   │   │   │ │ │
                  ┌───────┘    │   │   │   │ │ │
                  │ N          │   │   │   │ │ │
                  │ 1          │   │   │   │ │ │
         ┌────────▼────────┐   │   │   │   │ │ │
         │   dim_date      │   │   │   │   │ │ │
         │ ─────────────── │   │   │   │   │ │ │
         │ PK: date_id     │   │   │   │   │ │ │
         │ date            │   │   │   │   │ │ │
         │ day_name        │   │   │   │   │ │ │
         │ month_name      │   │   │   │   │ │ │
         │ quarter         │   │   │   │   │ │ │
         │ is_weekend      │   │   │   │   │ │ │
         └─────────────────┘   │   │   │   │ │ │
                               │   │   │   │ │ │
                      ┌────────┘   │   │   │ │ │
                      │ N          │   │   │ │ │
                      │ 1          │   │   │ │ │
            ┌─────────▼────────┐   │   │   │ │ │
            │  dim_country     │   │   │   │ │ │
            │ ──────────────── │   │   │   │ │ │
            │ PK: country_id   │   │   │   │ │ │
            │ country_code     │   │   │   │ │ │
            │ country_name     │   │   │   │ │ │
            │ region           │   │   │   │ │ │
            └──────────────────┘   │   │   │ │ │
                                   │   │   │ │ │
           (Similar connections for other dimensions...)
```

### Who Uses What?

**Operations Team:**
- Queries fact_revenue_daily for today's performance
- Joins with dim_app, dim_country for breakdowns
- Real-time monitoring dashboards

**Marketing Team:**
- Queries fact_cohort_retention for campaign LTV
- Uses dim_campaign for campaign attribution
- ROI calculations and budget optimization

**Executive Team:**
- Queries pre-aggregated marts (mart_app_performance)
- High-level summaries and trends
- Strategic decision-making

**Data Analysts:**
- Full access to all layers
- Can create custom queries joining facts and dimensions
- Ad-hoc analysis and deep dives

**AI Agent (Future):**
- Queries marts primarily (pre-aggregated, fast)
- Uses dimension metadata to understand what data means
- Converts natural language to SQL using table/column descriptions

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

**Last Updated:** October 19, 2025
**Status:** Planning Phase - Ready for Validation
**Next Action:** Begin Week 1 API capability testing
