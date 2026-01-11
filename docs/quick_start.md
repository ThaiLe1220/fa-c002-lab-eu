# Quick Start - Copy & Paste Commands

**Daily workflow commands for FA-C002 capstone development**

---

## Activate Environment

```bash
cd /Users/lehongthai/code_personal/fa-c002-lab
source .venv/bin/activate
```

---

## Data Collection (Capstone)

```bash
# Collect last 3 days from Adjust API → RAW_CAPSTONE.ADJUST_DAILY
python scripts/collect_adjust_capstone.py --days 3

# Collect last 3 days from AdMob API → RAW_CAPSTONE.ADMOB_DAILY
python scripts/collect_admob_capstone.py --days 3
```

---

## dbt Pipeline

### Run All Models

```bash
cd my_dbt_project && source ../.venv/bin/activate
dbt run --select staging      # Clean raw data
dbt run --select intermediate # Join sources
dbt run --select mart         # Build star schema
dbt test                      # Run all tests
```

### One-Liner (Full Build)

```bash
cd /Users/lehongthai/code_personal/fa-c002-lab/my_dbt_project && source ../.venv/bin/activate && dbt build
```

### Common Commands

```bash
dbt debug           # Test Snowflake connection
dbt run             # Run all models
dbt test            # Run all tests
dbt docs generate   # Generate docs
dbt docs serve      # View docs in browser
```

---

## Git Workflow

### Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### Regular Commits

```bash
git add .
git commit -m "feat: Description of change"
git push origin feature/your-feature-name
```

### Create PR and Merge

```bash
# After PR is approved on GitHub
git checkout main
git pull origin main
git merge feature/your-feature-name
git push origin main
```

**Test Requirement:** Need 2+ branches, 1+ merged PR, 3+ meaningful commits

---

## Troubleshooting

### Reset Virtual Environment

```bash
cd /Users/lehongthai/code_personal/fa-c002-lab
rm -rf .venv
uv venv --seed
uv add dbt-core dbt-snowflake snowflake-connector-python
```

### Check dbt Version

```bash
source /Users/lehongthai/code_personal/fa-c002-lab/.venv/bin/activate
dbt --version
```

### View Project Structure

```bash
cd /Users/lehongthai/code_personal/fa-c002-lab
tree -L 3 -I '.venv|.git' || find . -maxdepth 3 -not -path '*/\.venv/*' -not -path '*/\.git/*'
```

### Test Snowflake Connection

```bash
cd my_dbt_project && source ../.venv/bin/activate && dbt debug
```

---

## Reference

| Resource | Location |
|----------|----------|
| Environment setup | `docs/00_setup_guide.md` |
| Snowflake RSA setup | `docs/snowflake_setup.md` |
| Data schema | `fa-c002-capstone/docs/DATA_SCHEMA.md` |
| Business context | `docs/planning/data_strategy.md` |
