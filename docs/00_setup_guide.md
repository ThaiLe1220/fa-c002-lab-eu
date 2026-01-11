# Setup Reference

Technical reference for project setup and configuration.

**Schema:** `DB_T34.RAW_CAPSTONE` (raw) → `DB_T34.ANALYTICS` (mart)

## Environment Setup

```bash
# Project init
cd /Users/lehongthai/code_personal/fa-c002-lab
uv init --bare
git init && git branch -m main

# Virtual environment
uv venv --seed
uv add dbt-core dbt-snowflake

# dbt project
source .venv/bin/activate
dbt init my_dbt_project --skip-profile-setup
```

## Project Structure

```
fa-c002-lab/
├── my_dbt_project/
│   ├── models/
│   │   ├── 01_staging/
│   │   ├── 02_intermediate/
│   │   └── 03_mart/
│   └── dbt_project.yml
├── .venv/
└── pyproject.toml
```

## Snowflake Connection

**Location:** `~/.dbt/profiles.yml`

```yaml
my_dbt_project:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: <account_id>
      user: <username>
      authenticator: jwt
      private_key_path: /path/to/rsa_key.p8
      role: <role>
      database: DB_T34
      warehouse: <warehouse>
      schema: PUBLIC
      threads: 4
```

## Daily Commands

```bash
# Activate
cd my_dbt_project && source ../.venv/bin/activate

# Data collection (from project root)
python scripts/collect_adjust_capstone.py --days 3
python scripts/collect_admob_capstone.py --days 3

# dbt pipeline
dbt debug    # Test connection
dbt run      # Execute models
dbt test     # Run tests
```

## Git Workflow for Test

```bash
# Create feature branch
git checkout -b feature/data-pipelines

# Work and commit
git add .
git commit -m "feat: Add batch pipeline to Snowflake"

# Create PR
git push -u origin feature/data-pipelines
# Then create PR on GitHub

# Merge and cleanup
git checkout main
git merge feature/data-pipelines
```

**Test Requirement:** Need 2+ branches, 1+ merged PR, 3+ meaningful commits

---

## Key Metrics Reference

The pipeline tracks these metrics from Adjust API:

- `ad_revenue`, `ad_impressions` - Core ad performance
- `ad_revenue_total_D0`, `ad_impressions_total_D0` - Day 0 metrics (critical for ROAS)
- `network_cost` - Marketing spend
- `paid_impressions`, `subscrevnt_revenue` - Additional revenue streams

For full metric definitions, see `docs/planning/data_strategy.md`.
