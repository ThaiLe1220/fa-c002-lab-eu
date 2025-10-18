# FA-C002 Lab - Data Engineering Test Prep

**Mid-Course Test:** Oct 29 & Nov 1, 2025 | **11 days remaining**
**Target Score:** 70+ points (Pass: 50+)

## Quick Commands

```bash
# Activate environment
cd my_dbt_project && source ../.venv/bin/activate

# dbt workflow
dbt debug && dbt run && dbt test
```

## Current Status

**Learning Phase Complete:**
- ✅ Environment setup mastered
- ✅ Snowflake connection understood
- ✅ dbt fundamentals learned (mock data only)
- ✅ Git basics understood

**REAL PROJECT NOT STARTED YET:**
- ❌ Data choice not finalized
- ❌ All test requirements pending (0/100 pts)
- ❌ No production code written

**Next Phase: Planning & Data Selection**

## Test Requirements (All Pending - 0/100 pts)

| Section | Points | What's Needed |
|---------|--------|---------------|
| **1. Data Ingestion** | 35 | Git workflow + Python pipelines + Docker PostgreSQL |
| **2. Transformation** | 40 | Multi-layer dbt models + incremental + macro + ERD |
| **3. CI/CD** | 5 | GitHub Actions workflow |
| **4. Extra Features** | 20 | Optional (1-2 advanced features) |

**Full Details:** [Test Criteria](./docs/goal/midcourse_test_criteria.md)

## Planning Phase: Data Selection

**Key Decision: Choose business domain & dataset**

**Criteria:**
- Real-world applicable
- Multiple entities (customers, orders, products, etc.)
- Enables dimensional modeling (star schema)
- Supports business analysis questions
- Available via API or bulk download (500+ rows)

**Options to Consider:**
- E-commerce data
- Financial transactions
- Healthcare/fitness tracking
- Social media analytics
- IoT/sensor data
- Public datasets (Kaggle, government APIs, etc.)

## Project Structure

```text
fa-c002-lab/
├── CLAUDE.md                  # Project philosophy
├── docs/
│   ├── goal/                  # Test requirements
│   ├── 00_setup_guide.md      # Technical setup
│   └── quick_start.md         # Command reference
├── my_dbt_project/
│   └── models/
│       ├── 01_staging/        # ✅ stg_customers
│       ├── 02_intermediate/   # ❌ Empty
│       └── 03_mart/           # ❌ Empty
└── pipelines/                 # ❌ Doesn't exist yet
```

## Tech Stack

- **dbt 1.10.13** - Transformations
- **Snowflake** - Cloud warehouse (DB_T34)
- **Python 3.12** - Pipeline scripts
- **Docker** - PostgreSQL (to be set up)
- **GitHub Actions** - CI/CD (to be set up)

## Documentation

- [Setup Reference](./docs/00_setup_guide.md)
- [Quick Commands](./docs/quick_start.md)
- [Snowflake Config](./docs/snowflake_setup.md)
- [Sample Data](./docs/01_sample_data.md)
- [Staging Models](./docs/02_first_model.md)
- [Test Criteria](./docs/goal/midcourse_test_criteria.md)

## Philosophy

**Lean, test-driven, business-focused.** See [CLAUDE.md](./CLAUDE.md) for project coding principles.

---

**Last Updated:** October 18, 2025
