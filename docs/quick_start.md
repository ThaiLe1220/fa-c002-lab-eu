# Quick Start - Copy & Paste Commands

**For someone starting from scratch**

---

## Complete Setup (Copy All At Once)

```bash
# Navigate to project directory
cd /Users/lehongthai/code_personal/fa-c002-lab

# Initialize project with uv
uv init --bare
echo "# FA-C002 Lab - dbt Learning Project" > README.md

# Initialize Git
git init
git branch -m main
curl -s https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore -o .gitignore

# Create Python virtual environment
uv venv --seed

# Install dbt
uv add dbt-core dbt-snowflake

# Initialize dbt project
source .venv/bin/activate
dbt init my_dbt_project --skip-profile-setup

# Create model folder structure
cd my_dbt_project
rm -rf models/example
mkdir -p models/01_staging models/02_intermediate models/03_mart

# Create docs directory
cd ..
mkdir -p docs

# Verify everything
echo "✅ Setup complete!"
ls -la
```

---

## Daily Workflow

### Start Working
```bash
cd /Users/lehongthai/code_personal/fa-c002-lab/my_dbt_project
source ../.venv/bin/activate
```

### Run dbt Commands
```bash
dbt debug           # Test connection
dbt run             # Run all models
dbt test            # Run all tests
dbt docs generate   # Generate docs
dbt docs serve      # View docs in browser
```

---

## One-Line Commands

### Activate environment and test connection
```bash
cd /Users/lehongthai/code_personal/fa-c002-lab/my_dbt_project && source ../.venv/bin/activate && dbt debug
```

### Run all models and tests
```bash
cd /Users/lehongthai/code_personal/fa-c002-lab/my_dbt_project && source ../.venv/bin/activate && dbt run && dbt test
```

### Generate and serve documentation
```bash
cd /Users/lehongthai/code_personal/fa-c002-lab/my_dbt_project && source ../.venv/bin/activate && dbt docs generate && dbt docs serve
```

---

## Environment Variables (For Snowflake)

Create a `.env` file in the project root:

```bash
# .env file
export SNOWFLAKE_ACCOUNT="your-account"
export SNOWFLAKE_USER="your-username"
export SNOWFLAKE_PASSWORD="your-password"
export SNOWFLAKE_ROLE="your-role"
export SNOWFLAKE_DATABASE="your-database"
export SNOWFLAKE_WAREHOUSE="your-warehouse"
export SNOWFLAKE_SCHEMA="your-schema"
```

Load environment variables:
```bash
source .env
```

---

## Git Workflow

### Initial commit
```bash
cd /Users/lehongthai/code_personal/fa-c002-lab
git add .
git commit -m "Initial dbt project setup"
```

### Regular commits
```bash
git add .
git commit -m "Add staging models"
git push origin main
```

---

## Troubleshooting One-Liners

### Reset virtual environment
```bash
cd /Users/lehongthai/code_personal/fa-c002-lab && rm -rf .venv && uv venv --seed && uv add dbt-core dbt-snowflake
```

### Check if dbt is working
```bash
source /Users/lehongthai/code_personal/fa-c002-lab/.venv/bin/activate && dbt --version
```

### View project structure
```bash
cd /Users/lehongthai/code_personal/fa-c002-lab && tree -L 3 -I '.venv|.git' || find . -maxdepth 3 -not -path '*/\.venv/*' -not -path '*/\.git/*'
```

---

**Tip:** Save these commands in a text file for easy reference!
