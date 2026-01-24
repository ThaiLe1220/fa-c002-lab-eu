# Ameno Technologies Business Rules

## Company Overview

Ameno Technologies is a mobile gaming company headquartered in Vietnam. We develop and publish mobile games for iOS and Android platforms. Our revenue comes primarily from in-app advertising (AdMob) with supplementary revenue from subscriptions (Adjust tracking).

## Key Personnel

**Chi Linh - Business Performance Controller**
- Sets monthly UA (User Acquisition) targets
- Monitors app-level and campaign-level profitability
- Reports to executive team weekly on portfolio health

---

## ROAS Decision Framework

### What is ROAS?
ROAS (Return on Ad Spend) measures profitability of user acquisition:
- Formula: ROAS = (Ad Revenue / Network Cost) × 100
- D0 ROAS = Revenue from Day 0 (install day) / Cost
- D7 ROAS = Revenue from Days 0-7 / Cost

### ROAS Thresholds for Scaling Decisions

| D0 ROAS | Status | Action |
|---------|--------|--------|
| > 100% | Profitable | Scale spend by 20-50% |
| 80-100% | Marginal | Hold, monitor D7 recovery |
| 60-80% | Losing | Reduce spend by 30% |
| < 60% | Critical | Pause campaigns immediately |

### D7 Recovery Expectations
- Expected D7/D0 ratio: 1.3-1.5x (30-50% additional revenue by Day 7)
- If D0 = 80%, expect D7 = 104-120% (recoverable)
- If D0 = 60%, expect D7 = 78-90% (still losing, pause)

---

## CPI (Cost Per Install) Guidelines

### Benchmark CPIs by Platform
| Platform | Region | Target CPI | Alert Threshold |
|----------|--------|------------|-----------------|
| iOS | US | $2.00-3.00 | > $4.00 |
| iOS | SEA | $0.50-1.00 | > $1.50 |
| Android | US | $1.00-2.00 | > $2.50 |
| Android | SEA | $0.20-0.50 | > $0.80 |

### CPI Spike Investigation
If CPI increases > 30% week-over-week:
1. Check auction competition (holiday periods)
2. Check creative fatigue (>2 weeks same creative)
3. Check audience saturation
4. Check targeting changes

---

## eCPM Guidelines

### What is eCPM?
eCPM (Effective Cost Per Mille) = Revenue per 1,000 ad impressions
- Formula: eCPM = (Ad Revenue / Impressions) × 1000

### Benchmark eCPMs
| Format | Platform | Expected eCPM |
|--------|----------|---------------|
| Rewarded Video | iOS | $15-30 |
| Rewarded Video | Android | $10-20 |
| Interstitial | iOS | $8-15 |
| Interstitial | Android | $5-10 |
| Banner | All | $0.50-2.00 |

### eCPM Drop Investigation
If eCPM drops > 15% week-over-week:
1. Check ad network issues (AdMob status page)
2. Check seasonality (Q1 typically lowest)
3. Check fill rate changes
4. Check ad placement changes

---

## IMPDAU Guidelines

### What is IMPDAU?
IMPDAU = Impressions per Daily Active User
- Measures monetization intensity
- Too low = leaving money on table
- Too high = hurting retention

### Target IMPDAU Ranges
| Game Type | Target IMPDAU | Max IMPDAU |
|-----------|---------------|------------|
| Casual | 4-6 | 8 |
| Hypercasual | 6-10 | 15 |
| Midcore | 3-5 | 6 |

---

## Alert Severity Definitions

### Critical Alerts
- Require immediate action (within 1 hour)
- ROAS drops below 60%
- CPI spikes > 50%
- eCPM drops > 30%

### Warning Alerts
- Require action within 24 hours
- ROAS drops below 80%
- CPI increases 30-50%
- eCPM drops 15-30%

### Info Alerts
- For awareness, no immediate action
- Unusual patterns detected
- Milestone achievements

---

## Monthly Reporting Requirements

Chi Linh prepares these reports:
1. **Weekly Performance Report** (every Monday)
   - Portfolio ROAS by app
   - Top/Bottom 5 apps by revenue
   - Alert summary

2. **Monthly Business Review** (1st week of month)
   - Month-over-month revenue growth
   - UA spend efficiency
   - New app launches performance

3. **Executive Dashboard** (daily refresh)
   - Total revenue
   - Total spend
   - Portfolio ROAS
   - Active alerts

---

## Seasonal Patterns

### High CPM Periods
- Q4 (Oct-Dec): Holiday advertising, CPMs +30-50%
- Chinese New Year: SEA CPMs spike

### Low CPM Periods
- Q1 (Jan-Mar): Post-holiday slump, CPMs -20%
- Summer: Moderate, stable

### Budget Planning
- Increase UA budget in Q4 (higher LTV)
- Reduce in January (low eCPM, poor ROAS)
- Steady in Q2-Q3

---

## Data Sources

### AdMob (Source of Truth for Revenue)
- Ad revenue, impressions, clicks
- eCPM, fill rate
- Data freshness: T-1 (previous day)

### Adjust (Attribution & Cost)
- Installs, network cost
- CPI, campaign attribution
- Data freshness: T-1 (previous day)

### Streaming Alerts (Real-time)
- SPEND_SPIKE, ROAS_DROP alerts
- INSTALL_SURGE, ERROR_RATE
- Latency: ~1 minute
