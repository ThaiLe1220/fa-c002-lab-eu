# Mid-Course Test - Complete Criteria & Coverage Guide

**Test Date:** October 29 & November 01, 2025
**Duration:** 20 minutes
**Format:** Live demo to trainers
**Total Points:** 100
**Passing Score:** 50+ (minimum 50%)
**Course Weight:** 40% of final grade
**Critical:** MUST PASS to advance to Modules 03, 04, 05

---

## Table of Contents

1. [Overview & Importance](#overview--importance)
2. [Scoring Breakdown](#scoring-breakdown)
3. [Core Criteria Details](#core-criteria-details)
4. [Extra Features](#extra-features)
5. [Bonus Points](#bonus-points)
6. [Demo Preparation Checklist](#demo-preparation-checklist)
7. [Grading Impact](#grading-impact)

---

## Overview & Importance

The Mid-Course Test is a **mandatory checkpoint** after Module 2 that validates your mastery of foundational data engineering skills. It covers:

- **Modules Tested:** Module 01 & Module 02 only
- **Skills Focus:** Data ingestion, transformation, modeling, and basic CI/CD
- **Progression Gate:** Must pass to access M03, M04, M05

**What Happens After:**
- **Pass (≥50 pts):** Continue to advanced modules
- **Fail (<50 pts):** Retake modules in next cohort (30% fee applies)

---

## Scoring Breakdown

```
Total: 100 points

├─ CORE FUNCTIONALITY: 80 points (REQUIRED)
│  ├─ Section 1: Data Ingestion & Pipeline Foundation ........ 35 points
│  ├─ Section 2: Data Transformation & Modeling .............. 40 points
│  └─ Section 3: DevOps & CI Foundation ...................... 5 points
│
└─ EXTRA FEATURES: 20 points (OPTIONAL, 1-2 features max)
   └─ Each feature: max 10 points (must FULLY WORK)

BONUS OPPORTUNITIES:
├─ Tool Innovation Bonus ..................................... up to 10 points
└─ Peer Support Bonus ........................................ up to 15 points
```

**Key Insight:** You can pass with just core functionality (80 pts available, need 50 to pass)

---

## Core Criteria Details

### Section 1: Data Ingestion & Pipeline Foundation (35 points)

#### A. Project Setup & Data Collection (15 points)

**Git Workflow Requirements:**
- ✅ At least **2 branches** created in your repository
- ✅ At least **1 Pull Request (PR) or Merge Request (MR)** created AND merged
- ✅ At least **3 meaningful commits** with descriptive messages

**Data Collection Scripts (Python):**
- ✅ **Real-Time (Streaming) Pipeline Script**
  - Simulates row-by-row data ingestion
  - Collects data from API or streaming source
  - Must demonstrate incremental data collection

- ✅ **Batch Pipeline Script**
  - Ingests data in batches
  - Each batch must contain **≥500 rows**
  - Must demonstrate batch processing capability

**Live Demo Requirement:**
- Must show **NEW data** being collected during presentation
- Display timestamps to prove fresh data
- Execute scripts live and show results

**What to Show:**
```bash
# Example Demo Flow
1. Show git branch structure
2. Show merged PR history
3. Show commit log with meaningful messages
4. Execute real-time script → show new rows appearing
5. Execute batch script → show 500+ rows ingested
6. Display timestamps proving data is fresh
```

---

#### B. Data Ingestion (20 points)

**Local Database Setup:**
- ✅ **PostgreSQL database** running via Docker containerization
- ✅ Database accessible and operational during demo
- ✅ Proper connection configuration

**Batch Pipeline Implementation:**
- ✅ Script successfully moves **batch data** from local storage to **Snowflake**
- ✅ Data transfer verified in Snowflake
- ✅ Error handling implemented

**Real-Time Pipeline Implementation:**
- ✅ Script successfully moves data from **API/streaming source** to **PostgreSQL**
- ✅ Data appears in PostgreSQL database
- ✅ Incremental ingestion working properly

**Live Demo Requirement:**
- Execute both pipelines during presentation
- Show successful data landing in destinations
- Verify data with queries showing timestamps

**What to Show:**
```bash
# Example Demo Flow
1. Show Docker container running (docker ps)
2. Execute batch pipeline → data lands in Snowflake
3. Query Snowflake showing new data with timestamps
4. Execute real-time pipeline → data lands in PostgreSQL
5. Query PostgreSQL showing new data with timestamps
```

---

### Section 2: Data Transformation & Modeling (40 points)

#### A. Data Transformation Setup & Basic Models (30 points)

**dbt Testing Framework:**
- ✅ At least **2 data quality tests** implemented
  - Examples: unique, not_null, relationships, accepted_values
  - Custom tests via macros or schema.yml
  - Tests must execute successfully

**dbt Incremental Models:**
- ✅ At least **1 incremental model** or upsert model
  - Properly configured with unique_key
  - Demonstrates understanding of incremental processing
  - Shows efficient data processing

**dbt Custom Logic:**
- ✅ At least **1 custom transformation** via dbt macros
  - Custom SQL logic encapsulated in macro
  - Reusable transformation logic
  - Demonstrates macro understanding

**dbt Model Layering:**
- ✅ At least **3 dbt models** created across **at least 3 different layers**
  - **Raw layer:** Source data ingestion
  - **Staging layer:** Data cleaning and standardization
  - **Marts layer:** Business logic and aggregations
  - Proper folder structure and organization

**Live Demo Requirement:**
- Execute `dbt run` and show successful model builds
- Execute `dbt test` and show passing tests
- Query Snowflake to show transformed data
- Display lineage if possible

**What to Show:**
```bash
# Example Demo Flow
1. Show dbt project structure (models folder organization)
2. Show schema.yml with data quality tests defined
3. Show incremental model configuration
4. Show custom macro definition
5. Execute: dbt run --select model_name
6. Execute: dbt test
7. Query Snowflake showing transformed data
8. Show all 3 layers working together
```

**Example Model Structure:**
```
models/
├── raw/
│   └── raw_orders.sql              # Raw layer model
├── staging/
│   └── stg_orders.sql              # Staging layer model
└── marts/
    └── fct_daily_orders.sql        # Marts layer model (incremental)
```

---

#### B. Data Modeling (10 points)

**Modeling Approach Documentation:**
- ✅ Document your chosen **data modeling methodology**
  - **Dimensional Modeling** (star/snowflake schema)
  - **3NF (Third Normal Form)** (relational normalization)
  - **Data Vault** (hub, link, satellite patterns)
  - **One Big Table (OBT)** (denormalized wide table)

**Entity Relationship Diagram (ERD):**
- ✅ Create **ERD** showing your data model structure
  - Visual representation of tables/entities
  - Relationships between entities (1:1, 1:M, M:M)
  - Primary keys and foreign keys indicated
  - Clear and readable diagram

**Live Demo Requirement:**
- Display ERD during presentation
- Explain chosen modeling approach briefly
- Show how it aligns with your dbt models

**What to Show:**
```bash
# Example Demo Flow
1. Display ERD (can be image, diagram tool, or documentation)
2. Explain: "I chose Dimensional Modeling because..."
3. Point out fact tables and dimension tables
4. Show how dbt models implement this design
```

**Example Documentation:**
```markdown
# Data Modeling Approach: Dimensional Modeling

## Rationale
- Optimized for analytical queries
- Easy to understand for business users
- Efficient for Snowflake columnar storage

## Schema Design
- Fact Table: fct_orders (transaction grain)
- Dimensions: dim_customers, dim_products, dim_time
- Relationships: Star schema pattern
```

---

### Section 3: DevOps & CI Foundation (5 points)

#### A. Continuous Integration (CI) Implementation (5 points)

**GitHub Actions Workflow:**
- ✅ CI workflow configured in `.github/workflows/`
- ✅ At least **2 automated checks** implemented:
  - **Transformation pipeline validation** (dbt run)
  - **Data quality tests** (dbt test)
  - **Code linting** (sqlfluff, black, flake8)
  - **Unit tests** (pytest for Python code)

**Live Demo Requirement:**
- Show CI workflow executing successfully
- Display GitHub Actions interface with green checkmarks
- Explain what each check validates

**What to Show:**
```bash
# Example Demo Flow
1. Navigate to GitHub repository
2. Show .github/workflows/ci.yml file
3. Show GitHub Actions tab with recent runs
4. Show successful workflow execution (green checkmarks)
5. Briefly explain: "This runs dbt test and linting on every PR"
```

**Example CI Workflow Structure:**
```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
      - name: Setup Python
      - name: Install dependencies
      - name: Run dbt tests
      - name: Run linting
```

---

## Extra Features (20 points - OPTIONAL)

**Instructions:**
- Choose **1-2 advanced features** to implement
- Each feature worth **maximum 10 points**
- **All 3 criteria must be met** for ANY points:
  1. ✅ **Functionality:** Does it work as intended?
  2. ✅ **Implementation:** Is it properly implemented?
  3. ✅ **Complexity:** Does it demonstrate technical depth?

**Important:** Feature must **ACTUALLY WORK** - no partial credit for attempted implementation!

---

### Example Advanced Features

#### 1. Advanced dbt Features
- Custom dbt packages integration
- Complex incremental strategies (delete+insert, merge)
- Advanced testing frameworks (dbt-expectations)
- Custom materialization strategies
- Macro libraries for reusable logic
- Documentation with dbt docs generation

#### 2. Advanced Snowflake Features
- Snowflake Streams for CDC (Change Data Capture)
- Time Travel queries for data recovery
- Clustering keys for performance optimization
- Warehouse auto-scaling configuration
- Result caching strategies
- Zero-copy cloning for environments

#### 3. Advanced Docker Management
- Multi-stage Docker builds for optimization
- Docker Compose orchestration (multiple services)
- Custom Docker images with optimizations
- Container health checks and monitoring
- Volume management for persistence
- Network configuration for service communication

#### 4. Advanced Data Pipeline Features
- Real-time streaming with Apache Kafka
- Advanced error handling and retry logic
- Data lineage tracking and visualization
- Pipeline orchestration with Airflow/Prefect
- Data validation frameworks (Great Expectations)
- Monitoring and alerting systems

#### 5. Open Innovation
- Any advanced feature demonstrating technical skills
- Creative solutions to data engineering challenges
- Integration of modern tools and frameworks
- Performance optimizations
- Security enhancements
- Automation improvements

---

### How to Present Extra Features

**What to Show:**
```bash
# Example Demo Flow for Extra Feature
1. Briefly state: "I implemented [feature name]"
2. Show the code/configuration
3. Execute and demonstrate it working
4. Explain the complexity and value
5. Show results/output proving functionality
```

**Example: Kafka Streaming Feature**
```bash
1. "I implemented real-time streaming with Kafka"
2. Show Kafka topic configuration
3. Show producer sending messages
4. Show consumer receiving and processing
5. Show data landing in database with subsecond latency
6. Explain: "This enables true real-time analytics"
```

---

## Bonus Points

### 1. Tool Innovation Bonus (up to 10 points max)

**Eligibility:**
- Using **approved alternative tools** instead of curriculum default tools
- Must be from approved alternatives list

**Scoring:**
- Equal complexity to default tool: **5 points**
- More advanced than default tool: **10 points**

**Restrictions:**
- **No double-counting:** Cannot earn bonus for same tool twice across mid-course and capstone
- Only one application per tool across entire course

**Examples:**
- Using Prefect instead of Airflow
- Using ClickHouse instead of Snowflake
- Using Kubernetes instead of Docker Compose

---

### 2. Peer Support Bonus (up to 15 points)

**Eligibility:**
- Documented proof of supporting fellow students
- Teaching, mentoring, or helping classmates

**Scoring:**
- Up to **15 points for mid-course test**
- OR up to **10 points for capstone**
- **One-time application only** - choose where to apply

**Documentation Required:**
- Screenshots of help provided
- Testimonials from helped students
- GitHub collaboration evidence
- Study group leadership proof

---

## Demo Preparation Checklist

### Pre-Demo Technical Setup

**Environment Verification:**
- [ ] Docker Desktop running and containers healthy
- [ ] PostgreSQL container accessible (test connection)
- [ ] Snowflake account accessible and authenticated
- [ ] dbt profiles.yml configured correctly
- [ ] GitHub Actions workflows passing
- [ ] All scripts tested and working

**CLI Preparation:**
- [ ] Terminal windows prepared with commands ready
- [ ] Bash scripts for data collection tested
- [ ] dbt commands tested (dbt run, dbt test)
- [ ] SQL queries prepared for verification
- [ ] Timestamp queries ready to show fresh data

**Documentation Ready:**
- [ ] ERD diagram accessible (image or tool)
- [ ] Data modeling documentation open
- [ ] GitHub repository link ready
- [ ] GitHub Actions page bookmarked

**Test Run:**
- [ ] Complete full demo once before test day
- [ ] Time yourself (must be under 20 minutes)
- [ ] Verify all components work end-to-end
- [ ] Have backup plan for common failures

---

### Demo Execution Strategy

**Time Allocation (20 minutes total):**
```
0-5 min:   Section 1 - Data Ingestion & Pipelines
5-10 min:  Section 2 - Data Transformation & Modeling
10-12 min: Section 3 - CI/CD
12-15 min: Extra Features (if implemented)
15-20 min: Buffer for questions and issues
```

**Presentation Flow:**
1. **Start with working environment** - show Docker, databases ready
2. **Execute, don't explain first** - show it working, then briefly explain
3. **Use timestamps** - prove data is fresh and real
4. **Keep moving** - if something fails, move to next component
5. **Finish strong** - save best feature for last impression

**What NOT to Do:**
- ❌ Don't create fancy slides - waste of time
- ❌ Don't explain theory - show working code
- ❌ Don't troubleshoot live - have backups ready
- ❌ Don't go over 20 minutes - practice timing

**What TO Do:**
- ✅ Show working code and results
- ✅ Use prepared commands and queries
- ✅ Display timestamps proving fresh data
- ✅ Keep explanations brief and technical
- ✅ Demonstrate live execution

---

### Emergency Backup Plans

**If Docker PostgreSQL fails:**
- Have local PostgreSQL running as backup
- Or have connection string to cloud PostgreSQL ready

**If Snowflake connection fails:**
- Have screenshots of previous successful runs
- Have backup authentication method ready
- Check network/VPN before demo

**If dbt fails:**
- Have compiled SQL ready to show
- Have screenshots of previous successful runs
- Know which models are working vs. broken

**If CI workflow fails:**
- Have screenshots of previous successful runs
- Be able to run checks manually
- Explain what each check does

---

## Grading Impact

### Course Scoring Formula

```
Final Course Score = (Mid-Course Score × 0.40) + (Capstone Score × 0.60)
```

**Mid-Course Test Impact Examples:**

| Mid-Course | Capstone | Weighted Mid | Weighted Cap | Final Score | Outcome |
|------------|----------|--------------|--------------|-------------|---------|
| 80 pts | 80 pts | 32 | 48 | **80 pts** | Graduation |
| 70 pts | 80 pts | 28 | 48 | **76 pts** | Graduation |
| 60 pts | 70 pts | 24 | 42 | **66 pts** | Completion |
| 50 pts | 60 pts | 20 | 36 | **56 pts** | Completion |
| 45 pts | 90 pts | N/A | N/A | **FAIL** | Retake M01-M02 |

**Course Outcomes:**
- **70-100 points:** Course Graduation
  - Certificate of completion
  - Job placement assistance
  - Career support benefits

- **50-69 points:** Course Completion
  - Certificate of completion only
  - No job placement benefits

- **Below 50 points:** Course Failure
  - Must retake modules in next cohort
  - 30% retake fee applies
  - Cannot continue to M03-M05

---

### Strategic Scoring Guidance

**To Pass (50 points):**
- Focus on **core functionality only** (80 pts available)
- Ensure all 3 sections work properly
- Extra features not required to pass

**To Graduate (70+ final score):**
- Aim for **70+ on mid-course test**
- Or ensure strong capstone performance
- Consider implementing 1 extra feature well

**To Excel (90+ final score):**
- Aim for **80+ on mid-course test**
- Implement 1-2 extra features that fully work
- Consider bonus points opportunities
- Focus on code quality and documentation

---

## Success Criteria Summary

### Minimum Requirements to Pass (50 points)

**Must Have:**
1. ✅ Git workflow with branches, PRs, commits
2. ✅ Data collection scripts (real-time + batch) working
3. ✅ Docker PostgreSQL running
4. ✅ Batch pipeline → Snowflake working
5. ✅ Real-time pipeline → PostgreSQL working
6. ✅ At least 2 dbt models working
7. ✅ At least 1 dbt test passing
8. ✅ Basic data modeling documented
9. ✅ CI workflow configured (even if simple)

**Can Skip:**
- Extra features (nice to have, not required)
- Advanced dbt features
- Complex transformations
- Bonus points

---

### Recommended Requirements (70+ points)

**Should Have:**
1. ✅ All minimum requirements fully working
2. ✅ All 3 dbt layers implemented (raw, staging, marts)
3. ✅ At least 2 data quality tests passing
4. ✅ At least 1 incremental model working
5. ✅ At least 1 custom macro implemented
6. ✅ ERD diagram created and explained
7. ✅ CI workflow with 2+ checks passing
8. ✅ Clean, organized code structure

**Consider:**
- 1 extra feature that you're confident works
- Code quality and documentation
- Professional presentation

---

### Excellence Requirements (90+ points)

**Must Have:**
1. ✅ All recommended requirements perfectly executed
2. ✅ 1-2 extra features fully implemented and working
3. ✅ Advanced dbt features (expectations, packages, complex incrementals)
4. ✅ Comprehensive data quality testing
5. ✅ Well-documented code and models
6. ✅ Professional ERD and modeling documentation
7. ✅ Robust CI/CD pipeline with multiple checks
8. ✅ Clean demo execution under time

**Consider:**
- Bonus points opportunities (tool innovation, peer support)
- Code optimization and best practices
- Comprehensive error handling
- Performance considerations

---

## Final Checklist

### One Week Before Test

- [ ] All core functionality working end-to-end
- [ ] Practice demo once with timer
- [ ] Identify any gaps or missing requirements
- [ ] Test all components in clean environment
- [ ] Prepare ERD and documentation
- [ ] Set up GitHub Actions if not done

### One Day Before Test

- [ ] Complete full demo run-through with timer
- [ ] Verify all environment access (Snowflake, GitHub, Docker)
- [ ] Prepare all CLI commands in script files
- [ ] Screenshot evidence of working components as backup
- [ ] Check all credentials and connections
- [ ] Get good sleep (seriously!)

### Test Day Morning

- [ ] Restart Docker to ensure clean state
- [ ] Test all database connections
- [ ] Open all necessary browser tabs
- [ ] Prepare terminal windows with commands
- [ ] Have documentation ready to display
- [ ] Final environment check 30 min before demo
- [ ] Deep breath - you've got this!

---

## Key Takeaways

1. **Core functionality is king** - 80 points available, only need 50 to pass
2. **Show, don't tell** - working code beats explanations
3. **Fresh data required** - use timestamps to prove it
4. **Practice timing** - 20 minutes goes fast
5. **Have backups** - technology fails, be prepared
6. **Extra features only if confident** - must FULLY work or worth 0 points
7. **This test matters** - 40% of final grade + progression gate

**Focus Priority:**
1. Get core functionality working solidly
2. Practice demo execution and timing
3. Only then consider extra features
4. Prepare backup plans for failures

---

**Good luck on your mid-course test! You've got this!** 🚀

---

*Document created: 2025-10-18*
*Source: fa-c002-hub/capstone/capstone_midcourse_test.md*
*For questions or clarification, consult course materials or instructors*
