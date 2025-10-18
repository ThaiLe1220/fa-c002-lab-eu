# Module 2 Lab Setup Guide - Complete Command Reference

**Project:** FA-C002 Lab - dbt Learning Project
**Location:** `/Users/lehongthai/code_personal/fa-c002-lab`
**Date Started:** October 18, 2025

---

## Table of Contents

1. [Project Initialization](#step-1-project-initialization)
2. [Python Environment Setup](#step-2-python-environment-setup)
3. [dbt Installation](#step-3-dbt-installation)
4. [dbt Project Structure](#step-4-dbt-project-structure)
5. [Snowflake Configuration](#step-5-snowflake-configuration-pending)
6. [First Staging Model](#step-6-first-staging-model-pending)
7. [Testing and Validation](#step-7-testing-and-validation-pending)

---

## Prerequisites

- macOS (Darwin 24.6.0)
- `uv` package manager installed
- Snowflake account with access credentials
- Git installed
- Python 3.12+

---

## Step 1: Project Initialization

### 1.1 Navigate to Project Directory

```bash
cd /Users/lehongthai/code_personal/fa-c002-lab
```

**What it does:** Changes to your project directory.

---

### 1.2 Initialize uv Project

```bash
uv init --bare
```

**What it does:**
- Creates a minimal Python project structure
- Generates `pyproject.toml` for dependency management
- Sets up the project without a sample Python file

**Output:**
```
Initialized project `fa-c002-lab`
```

**Files created:**
- `pyproject.toml`

---

### 1.3 Create README

```bash
echo "# FA-C002 Lab - dbt Learning Project" > README.md
```

**What it does:** Creates a README file with project title.

---

### 1.4 Initialize Git Repository

```bash
git init
```

**What it does:**
- Initializes a new Git repository
- Creates `.git/` directory for version control

**Output:**
```
Initialized empty Git repository in /Users/lehongthai/code_personal/fa-c002-lab/.git/
```

---

### 1.5 Rename Default Branch to 'main'

```bash
git branch -m main
```

**What it does:** Renames the default branch from 'master' to 'main' (modern convention).

---

### 1.6 Download Python .gitignore Template

```bash
curl -s https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore -o .gitignore
```

**What it does:**
- Downloads the official Python `.gitignore` template
- Prevents committing Python cache files, virtual environments, etc.

**Files created:**
- `.gitignore` (4,562 bytes)

---

### 1.7 Verify Project Structure

```bash
ls -la
```

**Expected output:**
```
drwxr-xr-x   6 lehongthai  staff   192 Oct 18 09:35 .
drwxr-xr-x  19 lehongthai  staff   608 Oct 14 19:08 ..
drwxr-xr-x   9 lehongthai  staff   288 Oct 18 09:35 .git
-rw-r--r--   1 lehongthai  staff  4562 Oct 18 09:35 .gitignore
-rw-r--r--   1 lehongthai  staff    94 Oct 18 09:35 pyproject.toml
-rw-r--r--   1 lehongthai  staff    37 Oct 18 09:35 README.md
```

✅ **Checkpoint:** You should have `.git/`, `.gitignore`, `pyproject.toml`, and `README.md`.

---

## Step 2: Python Environment Setup

### 2.1 Create Virtual Environment

```bash
uv venv --seed
```

**What it does:**
- Creates a `.venv/` directory with isolated Python environment
- Includes pip (25.2) for package management
- Uses Python 3.12.2

**Output:**
```
Using CPython 3.12.2 interpreter at: /Users/lehongthai/miniconda3/bin/python3
Creating virtual environment with seed packages at: .venv
 + pip==25.2
Activate with: source .venv/bin/activate
```

**Files created:**
- `.venv/` directory

---

### 2.2 Activate Virtual Environment (Manual Step)

```bash
source .venv/bin/activate
```

**What it does:** Activates the virtual environment for the current terminal session.

**Note:** This needs to be run in each new terminal session.

---

## Step 3: dbt Installation

### 3.1 Install dbt-core and dbt-snowflake

```bash
uv add dbt-core dbt-snowflake
```

**What it does:**
- Installs `dbt-core` (1.10.13) - Core dbt functionality
- Installs `dbt-snowflake` (1.10.2) - Snowflake adapter for dbt
- Installs 71 total packages (all dependencies)

**Output:**
```
Resolved 77 packages in 2.12s
Prepared 60 packages in 21.56s
Installed 71 packages in 177ms
```

**Key packages installed:**
- `dbt-core==1.10.13`
- `dbt-snowflake==1.10.2`
- `snowflake-connector-python==3.18.0`
- `jinja2==3.1.6`
- `pyyaml==6.0.3`
- Many other dependencies...

**Files created/updated:**
- `pyproject.toml` (updated with dependencies)
- `uv.lock` (196,885 bytes - dependency lock file)

---

### 3.2 Verify dbt Installation

```bash
source .venv/bin/activate
dbt --version
```

**Expected output:**
```
Core:
  - installed: 1.10.13
  - latest:    1.10.13 - Up to date!

Plugins:
  - snowflake: 1.10.2 - Up to date!
```

✅ **Checkpoint:** dbt is installed and ready to use.

---

## Step 4: dbt Project Structure

### 4.1 Initialize dbt Project

```bash
cd /Users/lehongthai/code_personal/fa-c002-lab
source .venv/bin/activate
dbt init my_dbt_project --skip-profile-setup
```

**What it does:**
- Creates a new dbt project named `my_dbt_project`
- Skips the interactive profile setup (we'll configure manually)
- Creates standard dbt folder structure

**Output:**
```
Running with dbt=1.10.13
Creating dbt configuration folder at /Users/lehongthai/.dbt

Your new dbt project "my_dbt_project" was created!
```

**Files/folders created:**
```
my_dbt_project/
├── analyses/
├── macros/
├── models/
│   └── example/
├── seeds/
├── snapshots/
├── tests/
├── .gitignore
├── dbt_project.yml
└── README.md
```

---

### 4.2 Remove Example Models

```bash
cd my_dbt_project
rm -rf models/example
```

**What it does:** Removes the default example models (we'll create our own).

---

### 4.3 Create Proper Model Folder Structure

```bash
mkdir -p models/01_staging models/02_intermediate models/03_mart
```

**What it does:** Creates the three-layer dbt model structure:
- `01_staging/` - Clean and standardize raw data
- `02_intermediate/` - Business logic and transformations
- `03_mart/` - Analytics-ready tables (dimensions and facts)

---

### 4.4 Verify Folder Structure

```bash
ls -la models/
```

**Expected output:**
```
drwxr-xr-x   5 lehongthai  staff  160 Oct 18 09:37 .
drwxr-xr-x  11 lehongthai  staff  352 Oct 18 09:37 ..
drwxr-xr-x   2 lehongthai  staff   64 Oct 18 09:37 01_staging
drwxr-xr-x   2 lehongthai  staff   64 Oct 18 09:37 02_intermediate
drwxr-xr-x   2 lehongthai  staff   64 Oct 18 09:37 03_mart
```

✅ **Checkpoint:** dbt project structure is ready.

---

## Step 5: Snowflake Configuration (PENDING)

### 5.1 Snowflake Requirements

Before proceeding, gather these Snowflake details:

1. **Account Identifier** - Format: `abc12345.us-east-1` or `orgname-accountname`
2. **Username** - Your Snowflake username
3. **Authentication Method:**
   - Option A: Password
   - Option B: Private key authentication (recommended for production)
4. **Role** - e.g., `ACCOUNTADMIN`, `SYSADMIN`, `DEVELOPER`
5. **Warehouse** - e.g., `COMPUTE_WH`, `DEV_WH`
6. **Database** - e.g., `DEV_DB`, `ANALYTICS_DB`
7. **Schema** - e.g., `PUBLIC`, `STAGING`, `DBT_SCHEMA`

---

### 5.2 Create profiles.yml (TO BE COMPLETED)

**Location:** `~/.dbt/profiles.yml`

**Template (Password Authentication):**

```yaml
my_dbt_project:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: YOUR_ACCOUNT_IDENTIFIER
      user: YOUR_USERNAME
      password: YOUR_PASSWORD
      role: YOUR_ROLE
      database: YOUR_DATABASE
      warehouse: YOUR_WAREHOUSE
      schema: YOUR_SCHEMA
      threads: 4
      client_session_keep_alive: False
```

**Template (Private Key Authentication):**

```yaml
my_dbt_project:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: YOUR_ACCOUNT_IDENTIFIER
      user: YOUR_USERNAME
      private_key_path: /path/to/your/private_key.p8
      private_key_passphrase: "{{ env_var('SNOWFLAKE_PRIVATE_KEY_PASSPHRASE') }}"
      role: YOUR_ROLE
      database: YOUR_DATABASE
      warehouse: YOUR_WAREHOUSE
      schema: YOUR_SCHEMA
      threads: 4
      client_session_keep_alive: False
```

---

### 5.3 Test Snowflake Connection (TO BE COMPLETED)

```bash
cd /Users/lehongthai/code_personal/fa-c002-lab/my_dbt_project
source ../.venv/bin/activate
dbt debug
```

**Expected output:**
```
Configuration:
  profiles.yml file [OK found and valid]
  dbt_project.yml file [OK found and valid]

Required dependencies:
 - git [OK found]

Connection:
  account: YOUR_ACCOUNT
  user: YOUR_USER
  database: YOUR_DATABASE
  warehouse: YOUR_WAREHOUSE
  role: YOUR_ROLE
  schema: YOUR_SCHEMA

  Connection test: [OK connection ok]
```

---

## Step 6: First Staging Model (PENDING)

This section will be completed after Snowflake configuration.

---

## Step 7: Testing and Validation (PENDING)

This section will be completed after creating models.

---

## Quick Reference Commands

### Activate Virtual Environment
```bash
cd /Users/lehongthai/code_personal/fa-c002-lab
source .venv/bin/activate
```

### Navigate to dbt Project
```bash
cd /Users/lehongthai/code_personal/fa-c002-lab/my_dbt_project
```

### Common dbt Commands
```bash
dbt debug          # Test connection
dbt deps           # Install dependencies
dbt run            # Run all models
dbt test           # Run all tests
dbt docs generate  # Generate documentation
dbt docs serve     # Serve documentation locally
```

---

## Project Structure Overview

```
fa-c002-lab/
├── .git/                      # Git version control
├── .venv/                     # Python virtual environment
├── docs/                      # Documentation (this file)
├── my_dbt_project/           # dbt project
│   ├── models/
│   │   ├── 01_staging/       # Staging models
│   │   ├── 02_intermediate/  # Intermediate models
│   │   └── 03_mart/          # Mart models
│   ├── macros/               # Custom SQL macros
│   ├── seeds/                # CSV seed files
│   ├── snapshots/            # SCD Type 2 snapshots
│   ├── tests/                # Custom data tests
│   └── dbt_project.yml       # dbt configuration
├── .gitignore                # Git ignore rules
├── pyproject.toml            # Python dependencies
├── uv.lock                   # Dependency lock file
└── README.md                 # Project README
```

---

## Troubleshooting

### Issue: "dbt: command not found"
**Solution:** Activate virtual environment
```bash
source .venv/bin/activate
```

### Issue: "Connection refused" when running dbt debug
**Solution:** Check your Snowflake credentials in `~/.dbt/profiles.yml`

### Issue: "No such file or directory"
**Solution:** Make sure you're in the correct directory
```bash
cd /Users/lehongthai/code_personal/fa-c002-lab/my_dbt_project
```

---

## Next Steps

1. ✅ Project initialization complete
2. ✅ Python environment setup complete
3. ✅ dbt installation complete
4. ✅ dbt project structure created
5. ⏳ Configure Snowflake connection
6. ⏳ Create first staging model
7. ⏳ Run and test models

---

**Last Updated:** October 18, 2025
**Status:** Setup in progress - Ready for Snowflake configuration
