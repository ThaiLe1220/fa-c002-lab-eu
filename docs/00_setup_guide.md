# Setup Reference

Quick technical reference for project setup.

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

# Run
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
