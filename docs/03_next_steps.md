# Next Steps - When You're Ready to Continue

**Current Status**: You've completed dbt fundamentals with a working staging model. This document outlines what to do next when you're confident with the material so far.

---

## ✅ What You've Mastered

**Technical Setup:**
- ✅ Python virtual environment with uv
- ✅ dbt-core 1.10.13 installed and configured
- ✅ Snowflake connection with JWT authentication
- ✅ Git version control initialized

**dbt Fundamentals:**
- ✅ Project structure (staging/intermediate/mart layers)
- ✅ Source definitions (`_sources.yml`)
- ✅ SQL transformations with Jinja (`{{ source() }}`)
- ✅ Data quality tests (unique, not_null, accepted_values)
- ✅ dbt workflow (run → test → verify)

**Working Model:**
- ✅ `stg_customers` - 10 rows transformed and tested
- ✅ 8/8 tests passing
- ✅ Data cleaning (UPPER, LOWER)
- ✅ Calculated fields (customer_segment)
- ✅ Validation flags (has_valid_email)

---

## 🎯 Ready to Continue? Check These

Before moving to the next level, you should feel comfortable with:

- [ ] I can explain what `{{ source('raw', 'customers') }}` does
- [ ] I understand the difference between staging/intermediate/mart layers
- [ ] I can write a basic dbt model with SELECT and WHERE
- [ ] I know how to run `dbt run --select <model_name>`
- [ ] I can add a test to a model in YAML
- [ ] I understand why we use `UPPER()` and `LOWER()` for standardization
- [ ] I can explain what `materialized='view'` means
- [ ] I'm comfortable with the git workflow (add → commit)

**If you checked most boxes above**, you're ready for the next level.

---

## 🚀 Next Level: Intermediate Models (Lab 04 Complete)

**What you'll add:**

1. **Second Staging Model**: `stg_orders`
   - Clean raw order data
   - Standardize date formats
   - Add order status categorization

2. **First Intermediate Model**: `int_customer_orders`
   - JOIN customers and orders
   - Calculate aggregations (total_orders, avg_order_value)
   - Implement business logic (customer quality scoring)

3. **Advanced Patterns**:
   - Multi-source transformations
   - Aggregation functions (COUNT, SUM, AVG)
   - CASE statements for business rules
   - Incremental materialization

**Time estimate**: 1-2 hours
**Complexity**: Moderate (builds on what you know)

---

## 📋 Quick Continuation Commands

When you're ready to pick up where we left off:

```bash
# 1. Navigate to project and activate environment
cd /Users/lehongthai/code_personal/fa-c002-lab
source .venv/bin/activate

# 2. Verify everything still works
cd my_dbt_project
dbt debug
dbt run --select stg_customers
dbt test --select stg_customers

# 3. Ready to add more? Just say:
# "I'm ready to continue with intermediate models"
```

---

## 🗺️ Full Learning Roadmap

**Where you are now**: Week 1, Lab 03 ✅ + Lab 04 (simplified) ✅

**What's next**:

### Week 1 Completion
- **Lab 04 (Full)**: Intermediate models with JOINs and aggregations
- **Time**: 1-2 hours
- **You'll learn**: Multi-table transformations, business logic

### Week 2: Advanced Modeling
- **Lab 05**: Dimensional modeling (Facts and Dimensions)
- **Lab 06**: Incremental models for large datasets
- **Time**: 3-4 hours
- **You'll learn**: Star schema, performance optimization

### Week 3: Testing & Documentation
- **Lab 07**: Custom data quality tests
- **Lab 08**: dbt documentation generation
- **Time**: 2-3 hours
- **You'll learn**: Data quality framework, automated docs

### Week 4: Production Ready
- **Lab 09**: Deployment strategies
- **Lab 10**: CI/CD with GitHub Actions
- **Time**: 3-4 hours
- **You'll learn**: Production workflows, automation

**Total remaining**: ~10-15 hours of hands-on learning

---

## 💡 What to Review While Paused

**Strengthen your foundation by:**

1. **Read the learning modules** in `docs/learning/`:
   - Start with `00_overview.md` for the big picture
   - Deep dive into `03_dbt_fundamentals.md`
   - Review `04_data_modeling.md` for staging patterns

2. **Experiment with existing model**:
   - Try changing the `customer_segment` thresholds
   - Add a new calculated field
   - Add a new test
   - Run `dbt run` and `dbt test` after each change

3. **Explore Snowflake**:
   - Query `DB_T34.PUBLIC.STG_CUSTOMERS` directly
   - Compare it to `DB_T34.RAW.CUSTOMERS`
   - See how dbt transformed the data

4. **Practice commands**:
   - `dbt compile` - See the compiled SQL
   - `dbt run --select stg_customers` - Run specific model
   - `dbt test --select stg_customers` - Test specific model
   - `dbt run` - Run all models

---

## 🎓 Learning Resources

**Official Documentation:**
- [dbt Docs](https://docs.getdbt.com/) - Your reference guide
- [Snowflake Docs](https://docs.snowflake.com/) - Cloud warehouse guide

**Your Custom Documentation:**
- `docs/00_setup_guide.md` - Complete setup reference
- `docs/quick_start.md` - Quick command reference
- `docs/learning/` - 73,000 words of learning content

**Community:**
- [dbt Slack](https://www.getdbt.com/community/) - Ask questions
- [dbt Discourse](https://discourse.getdbt.com/) - Forum discussions

---

## 🚦 When You're Ready

**Just say one of these:**

- "I'm ready to continue with intermediate models"
- "Let's do Lab 04 full version"
- "I want to add the orders staging model"
- "Continue with next level"

**I'll pick up right where we left off** with step-by-step instructions for:
1. Creating sample order data
2. Building `stg_orders` model
3. Creating `int_customer_orders` with JOINs
4. Adding advanced tests
5. Documenting everything

---

## 📊 Your Progress

```
Module 2: Cloud Data Warehousing & Transformation

Week 1: dbt Fundamentals
├─ Lab 03: First Staging Model ✅ COMPLETE
│  └─ stg_customers with 8 tests passing
├─ Lab 04: Intermediate Models ⏸️ PAUSED
│  └─ Ready to continue when you are
│
Week 2: Advanced Modeling ⏭️ NEXT
Week 3: Testing & Documentation ⏭️ LATER
Week 4: Production Ready ⏭️ LATER
```

**You're ~25% through Module 2** - solid foundation built! 🎉

---

## 🎯 Bottom Line

**What to do now:**
1. Review the learning modules in `docs/learning/`
2. Get comfortable with current material
3. Experiment with the existing model
4. When confident, just say "I'm ready to continue"

**What happens next:**
1. We'll add order data to Snowflake
2. Create `stg_orders` staging model
3. Build `int_customer_orders` with JOINs and aggregations
4. Complete the full Lab 04 requirements
5. Move toward Week 2 when ready

**No rush** - master the fundamentals before advancing. The material isn't going anywhere, and solid foundations make everything easier later.

---

**Last Updated**: October 18, 2025
**Next Document**: Will be created when you continue
