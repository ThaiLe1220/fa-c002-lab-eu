# FA-C002 Lab - dbt Learning Project

Module 2: Cloud Data Warehousing & Transformation with dbt

---

## 📚 Documentation

- **[Complete Setup Guide](./docs/00_setup_guide.md)** - Step-by-step instructions with explanations
- **[Quick Start](./docs/quick_start.md)** - Copy-paste commands for fast setup
- **[Snowflake Setup](./docs/snowflake_setup.md)** - Snowflake connection configuration
- **[Sample Data](./docs/01_sample_data.md)** - Creating sample data in Snowflake
- **[First Model](./docs/02_first_model.md)** - Your first dbt staging model ✅

---

## 🎯 Project Goals

Learn modern data transformation techniques using:
- **dbt (data build tool)** - SQL-based transformation framework
- **Snowflake** - Cloud data warehouse
- **Dimensional modeling** - Star schema design
- **CI/CD** - Automated testing and deployment

---

## 🚀 Quick Start

### Activate Environment
```bash
cd /Users/lehongthai/code_personal/fa-c002-lab/my_dbt_project
source ../.venv/bin/activate
```

### Run dbt
```bash
dbt debug           # Test connection
dbt run             # Run models
dbt test            # Run tests
```

---

## 📁 Project Structure

```
fa-c002-lab/
├── docs/                      # Documentation
│   ├── 00_setup_guide.md     # Complete setup guide
│   └── quick_start.md         # Quick reference commands
├── my_dbt_project/           # dbt project
│   ├── models/
│   │   ├── 01_staging/       # Staging layer
│   │   ├── 02_intermediate/  # Business logic layer
│   │   └── 03_mart/          # Analytics layer
│   ├── macros/               # SQL macros
│   ├── tests/                # Data tests
│   └── dbt_project.yml       # Configuration
├── .venv/                    # Python virtual environment
├── pyproject.toml            # Dependencies
└── README.md                 # This file
```

---

## ✅ Setup Status

- [x] Project initialization
- [x] Python virtual environment
- [x] dbt installation (v1.10.13)
- [x] dbt project structure
- [x] Snowflake configuration ✅
- [x] Sample data created ✅
- [x] First staging model (`stg_customers`) ✅
- [x] All tests passing (8/8) ✅

## 🎉 What's Working

**Live in Snowflake:**
- Source: `DB_T34.RAW.CUSTOMERS` (10 rows)
- Model: `DB_T34.PUBLIC.STG_CUSTOMERS` (transformed data)
- Tests: 8 data quality tests all passing

---

## 🔗 Resources

- [dbt Documentation](https://docs.getdbt.com/)
- [Snowflake Documentation](https://docs.snowflake.com/)
- [Lab Instructions](../fa-c002-hub/content/M02/)

---

**Last Updated:** October 18, 2025
