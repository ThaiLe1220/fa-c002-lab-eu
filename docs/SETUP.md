# Setup Guide

## Prerequisites

- Python 3.11+
- uv (Python package manager)
- Snowflake account with RSA key authentication
- Access to AdMob and Adjust APIs

---

## Environment Setup

```bash
# Clone and navigate
cd /Users/lehongthai/code_personal/fa-c002-lab

# Create virtual environment
uv venv --seed
source .venv/bin/activate

# Install dependencies
uv add dbt-core dbt-snowflake snowflake-connector-python
```

---

## Snowflake RSA Key Setup

### 1. Get Connection Info

Run in Snowflake Worksheets:

```sql
SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE(),
       CURRENT_WAREHOUSE(), CURRENT_DATABASE();
```

### 2. Generate RSA Keys

```bash
mkdir -p ~/.snowflake/keys && cd ~/.snowflake/keys
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt
openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub
chmod 600 rsa_key.p8 rsa_key.pub
cat rsa_key.pub
```

### 3. Register Public Key in Snowflake

Run in Snowflake Worksheets:

```sql
CALL DB_UTILITIES.PUBLIC.p_set_rsa_key_for_current_user('-----BEGIN PUBLIC KEY-----
YOUR_PUBLIC_KEY_HERE
-----END PUBLIC KEY-----');
```

### 4. Configure dbt Profile

Create `~/.dbt/profiles.yml`:

```yaml
my_dbt_project:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: <ACCOUNT>
      user: <USER>
      authenticator: SNOWFLAKE_JWT
      private_key_path: ~/.snowflake/keys/rsa_key.p8
      role: <ROLE>
      warehouse: <WAREHOUSE>
      database: DB_T34
      schema: PUBLIC
      threads: 4
```

### 5. Test Connection

```bash
cd my_dbt_project
dbt debug
```

---

## Project Structure

```
fa-c002-lab/
├── .venv/                       # Virtual environment
├── my_dbt_project/
│   ├── dbt_project.yml
│   ├── models/
│   │   ├── 01_staging/
│   │   ├── 02_intermediate/
│   │   └── 03_mart/
│   └── macros/
├── scripts/
│   ├── collect_adjust_capstone.py
│   └── collect_admob_capstone.py
└── docs/
```

---

## Daily Commands

### Activate Environment

```bash
cd /Users/lehongthai/code_personal/fa-c002-lab
source .venv/bin/activate
```

### Data Collection

```bash
# Collect last 3 days from APIs to Snowflake RAW_CAPSTONE
python scripts/collect_adjust_capstone.py --days 3
python scripts/collect_admob_capstone.py --days 3
```

### dbt Pipeline

```bash
cd my_dbt_project

# Test connection
dbt debug

# Run all models
dbt run

# Run by layer
dbt run --select staging
dbt run --select intermediate
dbt run --select mart

# Run tests
dbt test

# Full build (run + test)
dbt build
```

### One-Liner (Full Pipeline)

```bash
cd /Users/lehongthai/code_personal/fa-c002-lab/my_dbt_project && source ../.venv/bin/activate && dbt build
```

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
source .venv/bin/activate
dbt --version
```

### View Project Structure

```bash
tree -L 3 -I '.venv|.git'
```

### Test Snowflake Connection

```bash
cd my_dbt_project && dbt debug
```

---

## Git Workflow

### Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### Commit Changes

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

**Test Requirement:** 2+ branches, 1+ merged PR, 3+ meaningful commits
