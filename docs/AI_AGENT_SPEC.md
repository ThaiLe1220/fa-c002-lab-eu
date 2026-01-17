# AI Agent Specification

## Part 1: Understanding The User

### Who is Chị Linh?

**Role:** Business Performance Controller

Chị Linh chịu trách nhiệm đảm bảo công ty profitable. Chị là cầu nối giữa data và business decisions.

**Quan trọng:** Chị KHÔNG phải người execute. UA team tự quyết định spend bao nhiêu, chạy campaign nào. Chị là người set direction, track progress, và alert khi có vấn đề.

### Tại sao vai trò này quan trọng?

Mobile app business có đặc thù:

1. **Burn rate cao:** Công ty spend ~$10K/ngày mua user. Nếu không track chặt, có thể mất $300K/tháng mà không biết.

2. **Feedback loop chậm:** Spend hôm nay, revenue tích lũy theo thời gian. Phải hiểu D0, D1, D7... để biết có lời không.

3. **Nhiều biến số:** 10 apps × 50+ countries × multiple ad networks = hàng trăm combinations. Không thể track manual hết.

Chị Linh là người "giữ cửa" - đảm bảo tiền spend đi đúng chỗ và sinh lời.

---

## Part 2: How Chị Linh Thinks

### Mental Model: The Profitability Equation

Mọi thứ chị làm đều xoay quanh một equation:

```text
Profit = Revenue - Cost

Mở rộng:
Profit = (IAA Revenue + IAP Revenue) - Network Cost

Mở rộng tiếp (đây là cách chị nghĩ):
Profit = (Users × Ads_per_user × Money_per_ad) + (Users × %_paying × ARPU) - (Users × Cost_per_user)
```

Từ equation này, chị derive ra các metrics:

| Component | Metric | Ý nghĩa |
| --------- | ------ | ------- |
| Users | Installs, DAU | Có bao nhiêu user? |
| Cost_per_user | CPI | Mua 1 user tốn bao nhiêu? |
| Ads_per_user | IMPDAU | Mỗi user xem bao nhiêu ads? |
| Money_per_ad | eCPM | Mỗi 1000 ads kiếm được bao nhiêu? |
| %_paying | Conversion rate | Bao nhiêu % user mua IAP? |
| ARPU | Revenue per paying user | User trả tiền thì trả bao nhiêu? |

**Insight:** Chị không nhìn metrics riêng lẻ. Chị nhìn chúng như các "lever" có thể pull để tăng profit.

### The Time Dimension: Why D0 Matters

Mobile app có đặc thù về user behavior:

```text
Day 0 (Install day): User hứng thú nhất, dùng nhiều nhất
Day 1: ~40% users quay lại
Day 7: ~15% users quay lại
Day 30: ~5% users quay lại
```

**Implication:** 70-80% tổng revenue đến từ Day 0.

**Vì vậy:** Nếu D0 ROAS < 100%, khả năng cao là campaign sẽ lỗ. D1+ retention chỉ recover được ~20-30% thêm.

**Cách chị nghĩ:**
- D0 ROAS > 100%: Tốt, có thể scale
- D0 ROAS 80-100%: Cần xem D7 retention có recover không
- D0 ROAS < 80%: Đang lỗ, cần pause hoặc optimize

### The Hierarchy: How Chị Drills Down

Khi có vấn đề, chị follow một pattern cố định:

```text
Level 0: Total (all apps, all countries)
         "Tổng ROAS tháng này là bao nhiêu? On track không?"
              ↓ Nếu off track
Level 1: By App
         "App nào đang kéo ROAS xuống?"
              ↓ Tìm được app có vấn đề
Level 2: By Country
         "Trong app đó, country nào có vấn đề?"
              ↓ Tìm được country
Level 3: By Ad Source
         "Traffic từ Facebook hay Google có vấn đề?"
              ↓ Tìm được source
Level 4: By Ad Unit / Creative
         "Ad nào không perform?"
              ↓
ROOT CAUSE → ACTION
```

**Insight:** Chị không random explore. Chị follow funnel từ macro → micro cho đến khi tìm được root cause.

**AI Agent implication:** Agent cần support drill-down flow này, không chỉ trả lời câu hỏi đơn lẻ.

---

## Part 3: The Decision Framework

### Khi nào chị alert team?

Chị có mental thresholds:

| Situation | Threshold | Action |
| --------- | --------- | ------ |
| ROAS drop | < 80% hoặc giảm > 20% so với tuần trước | Alert UA team pause/optimize |
| CPI spike | Tăng > 30% so với average | Check auction, creative fatigue |
| eCPM drop | Giảm > 15% | Check ad network issues, seasonality |
| Data mismatch | Adjust vs AdMob diff > 5% | Check data pipeline |

### Câu hỏi chị hỏi và logic đằng sau

**Câu hỏi 1:** "App nào spend nhiều nhất? Lời hay lỗ?"

```text
Logic:
- High spend + profitable = Scale thêm
- High spend + losing = Nguy hiểm, cần immediate action
- Low spend + profitable = Opportunity to scale
- Low spend + losing = Có thể chấp nhận hoặc kill
```

**Câu hỏi 2:** "Tại sao metrics thay đổi so với hôm qua?"

```text
Logic:
ROAS giảm có thể do:
├── Revenue giảm
│   ├── eCPM giảm (ad network trả ít hơn)
│   ├── IMPDAU giảm (user xem ít ads hơn)
│   └── DAU giảm (ít user hơn)
└── Cost tăng
    ├── CPI tăng (auction đắt hơn)
    └── Install volume tăng (spend nhiều hơn)

Chị cần biết FACTOR nào thay đổi để biết ACTION gì.
```

**Câu hỏi 3:** "Làm sao để break-even?"

```text
Logic:
ROAS = Revenue / Cost = (eCPM × IMPDAU) / (CPI × 1000)

Để ROAS = 100%:
- Option A: Giảm CPI (negotiate better rates, better targeting)
- Option B: Tăng eCPM (better ad placements, premium networks)
- Option C: Tăng IMPDAU (more ad units, better UX for ads)

Chị cần simulation: "Nếu CPI giảm 10%, ROAS sẽ thành bao nhiêu?"
```

**Câu hỏi 4:** "App đang lỗ có thể profitable không?"

```text
Logic:
Factors có thể thay đổi:
├── External (khó control)
│   ├── eCPM có thể tăng theo seasonality (Q4 thường cao)
│   ├── CPI có thể giảm nếu auction ít cạnh tranh
│   └── Market conditions
└── Internal (có thể control)
    ├── Product improvements → tăng IMPDAU
    ├── Better ad mediation → tăng eCPM
    └── Better targeting → giảm CPI

Chị cần data để justify: "Nếu dev team improve retention 10%, có profitable không?"
```

---

## Part 4: Metrics Deep Dive

### Tier 1: The Core Metrics (Chị check hàng ngày)

#### ROAS (Return on Ad Spend)

```text
Formula: d0_roas = ad_revenue_d0 / network_cost

Tại sao D0?
- 70-80% revenue từ Day 0
- Đây là leading indicator - biết sớm có lời không

Interpretation:
- > 120%: Excellent, scale aggressively
- 100-120%: Good, maintain và monitor
- 80-100%: Marginal, check D7 retention
- < 80%: Losing money, need action

Benchmark: Công ty target 120% D0 ROAS
```

#### CPI (Cost Per Install)

```text
Formula: cpi = network_cost / installs

Tại sao quan trọng?
- Đây là "giá mua 1 user"
- Varies significantly by country (US: $1-3, SEA: $0.1-0.3)
- Varies by ad network, creative quality, targeting

Factors ảnh hưởng CPI:
├── Auction competition (nhiều advertiser → đắt hơn)
├── Creative quality (CTR cao → CPI thấp)
├── Targeting precision (đúng audience → CPI thấp)
└── Seasonality (Q4 thường đắt vì holiday spend)
```

#### eCPM (Effective Cost Per Mille)

```text
Formula: ecpm = (ad_revenue × 1000) / ad_impressions

Tại sao quan trọng?
- Đây là "giá bán 1000 ads"
- Revenue = Impressions × eCPM / 1000
- Higher eCPM = more money per ad shown

Factors ảnh hưởng eCPM:
├── Country (US/EU cao, SEA/Africa thấp)
├── Ad format (rewarded video > interstitial > banner)
├── Ad network demand (more advertisers = higher eCPM)
├── User quality (engaged users = higher eCPM)
└── Seasonality (Q4 cao vì holiday ad spend)
```

### Tier 2: Diagnostic Metrics (Để drill down khi có vấn đề)

#### IMPDAU (Impressions Per DAU)

```text
Formula: d0_impdau = ad_impressions_d0 / daus

Ý nghĩa: Mỗi user xem bao nhiêu ads?

Tại sao quan trọng?
- Revenue = DAU × IMPDAU × eCPM / 1000
- Low IMPDAU = product issue (user không engage đủ để xem ads)
- High IMPDAU = có thể đang over-monetize (annoying users)

Healthy range: 3-6 ads/user/day
Warning: < 2 (low engagement) hoặc > 10 (over-monetizing)
```

#### IPM (Installs Per Mille)

```text
Formula: ipm = (installs × 1000) / paid_impressions

Ý nghĩa: Mỗi 1000 ad impressions mua được bao nhiêu installs?

Tại sao quan trọng?
- Đây là proxy cho "ad creative quality"
- High IPM = ads đang convert tốt
- Low IPM = creative fatigue hoặc wrong targeting

Relationship với CPI:
CPI = paid_eCPM / IPM × 1000
→ IPM cao = CPI thấp
```

#### paid_eCPM (Cost per 1000 UA impressions)

```text
Formula: paid_ecpm = (network_cost × 1000) / paid_impressions

Ý nghĩa: Giá mua 1000 impressions trên ad networks

Tại sao quan trọng?
- Khác với eCPM (earn), đây là cost để mua traffic
- paid_eCPM × IPM / 1000 = CPI
```

### Tier 3: Business Health Metrics

#### IAA Profit (In-App Advertising Profit)

```text
Formula: iaa_profit = ad_revenue - network_cost

Ý nghĩa: Lời/lỗ từ advertising business

Đây là core profit metric cho ad-supported apps.
```

#### IAP Profit (In-App Purchase Profit)

```text
Formula: iap_profit = subscrevnt_revenue (subscription + one-time purchases)

Ý nghĩa: Revenue từ users trả tiền

Target của công ty: IAP = 30% of total revenue
Current reality: Chủ yếu từ IAA (SDK tracking IAP chưa complete)
```

#### Gross Profit

```text
Formula: gross_profit = iaa_profit + iap_profit

Ý nghĩa: Tổng lợi nhuận gộp

Đây là ultimate metric - công ty có lời không?
```

### Tier 4: Target & Simulation Metrics

#### 100% d0 RPM (Break-even RPM)

```text
Formula: 100%_d0_rpm = cpi × 1000 / d0_impdau

Ý nghĩa: RPM cần đạt để break-even (ROAS = 100%)

Use case: "Với CPI = $0.15 và IMPDAU = 4, cần RPM = $37.5 để break-even"

Chị dùng để:
- So sánh với actual RPM → biết còn thiếu bao nhiêu
- Set target cho monetization team
```

#### 100% CPI (Break-even CPI)

```text
Formula: 100%_cpi = d0_rpm × d0_impdau / 1000

Ý nghĩa: CPI tối đa có thể chấp nhận để break-even

Use case: "Với RPM = $30 và IMPDAU = 4, CPI max = $0.12"

Chị dùng để:
- Set bid cap cho UA team
- Evaluate market có còn profitable không
```

---

## Part 5: Data Quality & Reconciliation

### Tại sao cần 2 data sources?

```text
AdMob (Google):
- Source of truth cho REVENUE (tiền thật vào bank)
- Nhược điểm: Không có attribution (không biết user từ đâu tới)

Adjust (Attribution):
- Source of truth cho ATTRIBUTION (user từ Facebook hay Google)
- Có thể estimate revenue nhưng không chính xác 100%
- Có D0 metrics (biết revenue theo ngày install)
```

### Reconciliation Logic

```text
% diff rev = |adjust_revenue - admob_revenue| / admob_revenue

Healthy: < 5% difference
Warning: 5-10% difference
Critical: > 10% difference (data pipeline có vấn đề)

Nếu mismatch lớn:
1. Check API collection có fail không
2. Check timezone differences
3. Check currency conversion
4. Check app store ID mapping
```

---

## Part 6: AI Agent Requirements

### Positioning

**Bổ sung Looker, không thay thế.**

| Looker (visual) | AI Agent (conversational) |
| --------------- | ------------------------- |
| Xem trends, patterns | Hỏi câu hỏi cụ thể |
| Filter và explore | Natural language query |
| Static dashboards | Dynamic drill-down |
| Chị tự interpret | Agent giải thích WHY |

### Phase 1: Query (Foundation)

**Goal:** Trả lời câu hỏi data cơ bản bằng natural language

**Example queries:**

```text
"ROAS Thailand hôm qua bao nhiêu?"
→ Agent query fact table, return: "D0 ROAS Thailand hôm qua là 93%, giảm 5% so với hôm kia"

"App nào spend nhiều nhất tuần này?"
→ Agent aggregate by app, return top 3 với cost và ROAS

"So sánh CPI Vietnam vs Thailand 7 ngày qua"
→ Agent return comparison table với trend
```

**Success criteria:**
- Accuracy match với Looker
- Response < 10 seconds
- Chị có thể hỏi 10 câu cơ bản không cần SQL

### Phase 2: Explain (WHY)

**Goal:** Giải thích tại sao metrics thay đổi

**Example:**

```text
"Tại sao ROAS giảm 15% so với tuần trước?"

Agent analysis:
1. Check revenue change: -8%
2. Check cost change: +5%
3. Drill into revenue: eCPM stable, IMPDAU giảm 10%
4. Drill into IMPDAU: App X giảm 25%, app khác stable

→ Response: "ROAS giảm 15% chủ yếu do:
   1. Cost tăng 5% (CPI Thailand tăng 12%)
   2. Revenue giảm 8% (IMPDAU app X giảm 25%)
   Recommend: Check app X có update gì không, và review Thailand bidding"
```

**Success criteria:**
- Giảm thời gian drill-down từ 30 phút → 5 phút
- Chị trust explanation đủ để action

### Phase 3: Alert (Proactive)

**Goal:** Auto-detect anomalies và alert trước khi chị check

**Example alerts:**

```text
"🚨 Thailand ROAS dropped to 72% (3-day average)
   - Below 80% threshold
   - Main factor: CPI spiked 28%
   - Recommend: Review bid caps"

"⚠️ App X IMPDAU dropped 20% since yesterday
   - Check if recent app update affected ad display
   - Revenue impact: ~$500/day"

"✅ Vietnam performing well: ROAS 135%
   - CPI stable, eCPM up 8%
   - Opportunity: Consider increasing budget 20%"
```

**Success criteria:**
- Detect issues before morning check
- < 3 false positives per week
- Chị trust alerts đủ để forward to team

### Phase 4: Simulate (WHAT IF)

**Goal:** Answer hypothetical questions

**Example:**

```text
"Nếu CPI Thailand giảm 15%, ROAS sẽ thành bao nhiêu?"
→ Agent calculate: Current ROAS 93% × (1/0.85) = 109%
→ "Nếu CPI giảm 15%, ROAS sẽ tăng từ 93% lên ~109%"

"Cần eCPM bao nhiêu để break-even với CPI hiện tại?"
→ Agent calculate break-even eCPM
→ "Với CPI $0.15 và IMPDAU 4.2, cần eCPM $35.7 để break-even (hiện tại $31.2)"
```

**Success criteria:**
- Calculations accurate
- Chị dùng để negotiate targets với team

---

## Part 7: Data Mapping

### Available Data (Snowflake)

**ADMOB_DAILY:**

| Column | Maps to | Notes |
| ------ | ------- | ----- |
| ESTIMATED_EARNINGS | ad_revenue | Source of truth for money |
| AD_IMPRESSIONS | ad_impressions | For eCPM calculation |
| AD_CLICKS | ad_clicks | For CTR |
| APP_STORE_ID | app identifier | Join key |
| COUNTRY_CODE | country | Breakdown dimension |
| DATE | date | Time dimension |

**ADJUST_DAILY:**

| Column | Maps to | Notes |
| ------ | ------- | ----- |
| NETWORK_COST | cost | UA spend |
| INSTALLS | installs | New users |
| DAUS | dau | Active users |
| AD_REVENUE | adjust_revenue | For reconciliation |
| AD_IMPRESSIONS | adjust_impressions | For reconciliation |
| AD_REVENUE_TOTAL_D0 | d0_revenue | Day 0 revenue |
| AD_IMPRESSIONS_TOTAL_D0 | d0_impressions | Day 0 impressions |
| PAID_IMPRESSIONS | paid_impressions | UA impressions |
| SUBSCREVNT_REVENUE | iap_revenue | In-app purchases |

### Metrics Calculation Reference

```sql
-- Core metrics
d0_roas = ad_revenue_d0 / network_cost
cpi = network_cost / installs
ecpm = (admob_revenue * 1000) / admob_impressions
d0_impdau = ad_impressions_d0 / daus

-- Diagnostic metrics
ipm = (installs * 1000) / paid_impressions
paid_ecpm = (network_cost * 1000) / paid_impressions
arpdau = admob_revenue / daus

-- Profit metrics
iaa_profit = admob_revenue - network_cost
gross_profit = admob_revenue + subscrevnt_revenue - network_cost

-- Break-even simulation
break_even_rpm = cpi * 1000 / d0_impdau
break_even_cpi = d0_rpm * d0_impdau / 1000

-- Data quality
rev_diff_pct = abs(adjust_revenue - admob_revenue) / admob_revenue
```

---

## Part 8: Out of Scope (Current)

### Data limitations

- **No Ad Source breakdown:** Data chỉ có total, không split Facebook/Google/TikTok
- **No Ad Unit breakdown:** Không biết banner vs interstitial vs rewarded
- **No cohort analysis:** Chỉ có daily aggregate, không track user cohorts over time
- **IAP tracking incomplete:** SDK chưa capture đầy đủ

### Functional limitations

- **Read-only:** Agent chỉ query và explain, không execute actions
- **Daily batch:** Data update 1 lần/ngày, không real-time
- **No forecasting:** Chỉ analyze historical, không predict future

### Future considerations

- Integrate Ad Source data từ Facebook/Google APIs
- Add cohort tracking (D1, D7, D30 retention)
- Real-time alerting via Slack/Email
- Action suggestions với confidence scores

---

## Part 9: Success Metrics

### Phase 1 Success

| Metric | Target | How to measure |
| ------ | ------ | -------------- |
| Query accuracy | 100% match Looker | Spot check 20 queries |
| Response time | < 10 seconds | Monitor p95 latency |
| User adoption | Chị dùng daily | Usage logs |

### Phase 2+ Success

| Metric | Target | How to measure |
| ------ | ------ | -------------- |
| Time saved | 30 min → 5 min drill-down | User feedback |
| Alert accuracy | < 3 false positives/week | Track alert outcomes |
| Trust level | Chị action without Looker verify | User feedback |

---

## Appendix: Chị Linh's Actual Questions

Từ meeting notes, đây là các câu hỏi thực tế chị sẽ hỏi:

1. "App nào spend nhiều nhất, với cost như hiện tại thì lời hay lỗ?"
2. "Spend đẩy lên thì ảnh hưởng đến các metrics khác như thế nào?"
3. "Tại sao metrics hôm nay tăng/giảm so với hôm qua?"
4. "Làm sao để hoà vốn?"
5. "App này trước giờ mình đang lỗ, có khả năng hoà vốn hay lời lại không?"
6. "Factor nào dẫn đến những sự thay đổi mà mình quan sát được?"
7. "Installs over time by country đang như thế nào?"
8. "So sánh CPI và 100% CPI để biết còn room không?"
9. "Revenue by country breakdown?"
10. "Data có khớp không? Adjust vs AdMob diff bao nhiêu %?"
