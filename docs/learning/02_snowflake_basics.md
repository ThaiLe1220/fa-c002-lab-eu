# Module 2: Snowflake & Cloud Data Warehousing

**What you learned about cloud data warehouses and Snowflake**

---

## 🎯 Core Concepts Learned

### 1. Cloud Data Warehouse Architecture

**Traditional vs Cloud:**

```
Traditional Data Warehouse (On-Premise):
- Fixed hardware costs
- Manual scaling
- Limited concurrency
- Tight coupling of compute + storage

Cloud Data Warehouse (Snowflake):
- Pay-per-use pricing
- Auto-scaling
- Unlimited concurrency
- Separated compute + storage ✨
```

**Why this matters:**
- **Cost:** Only pay for what you use
- **Scale:** Handle any data size
- **Speed:** Add compute when needed
- **Flexibility:** Different teams don't compete for resources

---

### 2. Snowflake's Key Innovation: Separation of Compute & Storage

**What you learned:**

```
STORAGE LAYER (Database)
    ↓
    Stores all your data
    Charged by TB/month
    Always available
    ↓
COMPUTE LAYER (Warehouse)
    ↓
    Runs queries
    Charged by second of use
    Can have multiple sizes
    Can suspend when not in use
```

**Real-world example from your setup:**
- **Storage:** `DB_T34.RAW.CUSTOMERS` - Data stored here
- **Compute:** `WH_T34` - Warehouse that runs queries
- **Result:** Can stop WH_T34, data still safe in DB_T34

**Why this is revolutionary:**
- Scale compute independently of data
- Stop warehouse = stop charges (data remains)
- Multiple warehouses can access same data

---

## 🔐 Authentication Deep Dive

### What You Implemented: JWT Authentication

**Method 1: Password (NOT USED)**
```yaml
user: T34
password: "my_password"  # ❌ Less secure, stored in plain text
```

**Method 2: Private Key (WHAT YOU USED)** ✅
```yaml
user: T34
authenticator: SNOWFLAKE_JWT
private_key_path: /Users/lehongthai/.snowflake/keys/rsa_key.p8
```

---

### RSA Key Pair Authentication - Step by Step

**What you did:**

```bash
# 1. Generated private key
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt

# 2. Extracted public key
openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub

# 3. Set permissions
chmod 600 rsa_key.p8  # Only you can read
```

**How it works:**
1. You keep private key (secret)
2. Snowflake gets public key (sharable)
3. dbt signs request with private key
4. Snowflake verifies with public key
5. If match = authenticated ✅

**Why JWT over password:**
- ✅ No password in files
- ✅ Can't be accidentally leaked
- ✅ Can rotate keys without changing code
- ✅ Industry best practice for automation
- ✅ Required for production systems

---

## 📊 Snowflake Objects You Learned

### 1. Database
**What:** Top-level container for schemas
**Your database:** `DB_T34`
**Purpose:** Organizational boundary, permissions

### 2. Schema
**What:** Container for tables within database
**Your schemas:**
- `RAW` - Source data
- `PUBLIC` - Transformed data (dbt output)

**Purpose:** Logical separation of data layers

### 3. Warehouse
**What:** Compute resource that runs queries
**Your warehouse:** `WH_T34`
**Purpose:** Actually executes SQL

### 4. Role
**What:** Collection of permissions
**Your role:** `RL_T34`
**Purpose:** What you're allowed to do

---

### Hierarchy You Learned

```
Account: LNB11254
    ↓
Database: DB_T34
    ↓
Schemas: RAW, PUBLIC
    ↓
Tables: CUSTOMERS, STG_CUSTOMERS
    ↓
Columns: customer_id, customer_name, etc.
```

**Practical impact:**
- Fully qualified table name: `DB_T34.RAW.CUSTOMERS`
- Can have same table name in different schemas
- Permissions at any level

---

## 🔧 Connection Configuration Deep Dive

### profiles.yml - The Connection File

**Location:** `~/.dbt/profiles.yml`

**What you configured:**
```yaml
my_dbt_project:          # Profile name (matches dbt_project.yml)
  target: dev            # Which environment to use
  outputs:               # Can have multiple (dev, prod, etc.)
    dev:
      type: snowflake    # Database type
      account: LNB11254  # Your Snowflake account
      user: T34          # Your username
      authenticator: SNOWFLAKE_JWT  # Auth method
      private_key_path: /Users/lehongthai/.snowflake/keys/rsa_key.p8
      role: RL_T34       # What you can do
      warehouse: WH_T34  # Compute to use
      database: DB_T34   # Where data lives
      schema: PUBLIC     # Default schema
      threads: 4         # Parallel queries
      client_session_keep_alive: False
      query_tag: dbt_learning  # Tag for monitoring
```

---

### Connection Parameters Explained

**account:**
- Format: Usually `XXXXXXXX` or `orgname-accountname`
- Where: Snowflake URL: `https://LNB11254.snowflakecomputing.com`
- Purpose: Identifies your Snowflake instance

**user:**
- Your Snowflake username
- Case-sensitive
- Purpose: Identifies who is connecting

**role:**
- Set of permissions
- Purpose: What operations you can perform
- Can switch roles during session

**warehouse:**
- Compute resource to use
- Can be different sizes (X-Small to 6X-Large)
- Purpose: Runs your queries
- **Cost impact:** Larger = faster but more expensive

**database & schema:**
- Default location for operations
- Can override in SQL: `FROM other_db.other_schema.table`
- Purpose: Convenience, don't have to fully qualify

**threads:**
- How many models dbt runs in parallel
- More threads = faster (if warehouse can handle it)
- Typical: 4-8 for development

**query_tag:**
- Labels your queries in Snowflake
- Purpose: Monitoring, cost tracking, debugging
- Shows up in query history

---

## 🎓 Key Concepts You Mastered

### 1. Environment Separation

**What you learned:**
```yaml
outputs:
  dev:        # Development environment
    warehouse: WH_T34_DEV
    schema: DEV_SCHEMA

  prod:       # Production environment
    warehouse: WH_T34_PROD
    schema: PROD_SCHEMA
```

**Why it matters:**
- Test changes in dev without affecting prod
- Different costs for different environments
- Can use smaller warehouses for dev

---

### 2. Connection Testing

**Command you learned:**
```bash
dbt debug
```

**What it tests:**
```
✅ profiles.yml exists and is valid
✅ dbt_project.yml exists and is valid
✅ Git is installed
✅ Can connect to Snowflake
✅ Can run test query
```

**Why this matters:**
- Catch configuration issues immediately
- Verify permissions work
- Ensure warehouse is accessible
- Test before running expensive queries

---

### 3. Security Best Practices

**What you applied:**

1. **No credentials in code:**
   - ✅ Private key separate from project
   - ✅ profiles.yml in home directory (not in git)
   - ✅ Can use environment variables for extra security

2. **Restrictive permissions:**
   ```bash
   chmod 600 rsa_key.p8  # Only owner can read/write
   ```

3. **Key rotation ready:**
   - Can generate new keys anytime
   - Update in Snowflake
   - No code changes needed

---

## 💡 Real-World Insights

### Insight 1: Compute is Expensive, Storage is Cheap

**What you learned:**
- **Storage:** ~$40/TB/month
- **Compute:** $2-$512/hour depending on size

**Practical impact:**
- Store lots of data (cheap)
- Optimize queries to use less compute time
- Suspend warehouses when not in use
- Your small warehouse costs ~$2/hour, but only while running

---

### Insight 2: Multiple Warehouses, Same Data

**What this enables:**
```
WH_DBT (Small)     ─┐
                    ├─→ DB_T34.RAW.CUSTOMERS
WH_ANALYTICS (Large)─┘
```

**Use cases:**
- dbt runs on small warehouse
- Analysts use large warehouse for complex queries
- Both access same data
- Don't compete for resources

---

### Insight 3: Snowflake's "Time Travel"

**What you discovered (when checking data):**
- Snowflake keeps deleted data for 1-90 days
- Can query historical data: `SELECT * FROM table AT(OFFSET => -3600)`
- Can recover accidentally deleted tables

**Why it matters:**
- Mistakes are recoverable
- Can audit data changes
- Compliance and debugging

---

## 🚫 Common Pitfalls You Avoided

### Pitfall 1: Leaving Warehouses Running
❌ **DON'T:** Forget to suspend warehouse
```sql
ALTER WAREHOUSE WH_T34 SUSPEND;  -- Manually suspend
```

✅ **DO:** Set auto-suspend
```sql
ALTER WAREHOUSE WH_T34 SET AUTO_SUSPEND = 60;  -- Suspend after 1 minute
```

**Your setup:** dbt closes connection after each run (auto-suspend)

---

### Pitfall 2: Using Production Warehouse for Dev
❌ **DON'T:** Use same warehouse for dev and prod
✅ **DO:** Separate warehouses (you can configure this later)

**Why:** Dev queries shouldn't slow down production users

---

### Pitfall 3: Storing Passwords in Files
❌ **DON'T:**
```yaml
password: "MyPassword123"  # In profiles.yml
```

✅ **DO:**
```yaml
private_key_path: /path/to/key  # Using key-pair auth
```

**What you did:** JWT authentication with private key ✅

---

## 📊 Cost Awareness You Gained

### What Costs Money in Snowflake

1. **Storage:** Amount of data stored
   - Your 10-row table: Negligible
   - Charged monthly by TB

2. **Compute:** Warehouse running time
   - Charged per-second
   - Different sizes = different costs
   - Your dbt runs: Seconds of small warehouse

3. **Cloud Services:** Metadata operations
   - Usually < 10% of compute costs
   - Includes: authentication, optimization, metadata

**Your project costs:** Essentially $0 (free tier or minimal usage)

---

## 🎯 Skills You Can Transfer

### To Other Cloud Data Warehouses
- ✅ BigQuery (Google)
- ✅ Redshift (AWS)
- ✅ Synapse (Azure)

**Concepts that transfer:**
- Compute/storage separation
- Connection configuration
- Authentication methods
- Cost optimization strategies

---

### To General Cloud Infrastructure
- ✅ IAM and authentication
- ✅ Resource management
- ✅ Cost optimization
- ✅ Security best practices

---

## 🎓 Quiz Yourself

1. **Why separate compute and storage?**
   <details>
   <summary>Answer</summary>
   Scale independently, stop compute while keeping data, multiple compute resources can access same data
   </details>

2. **What does SNOWFLAKE_JWT do?**
   <details>
   <summary>Answer</summary>
   Uses public-key cryptography for authentication instead of passwords
   </details>

3. **What is a warehouse in Snowflake?**
   <details>
   <summary>Answer</summary>
   Compute resource that runs queries (not storage)
   </details>

4. **Why use query_tag?**
   <details>
   <summary>Answer</summary>
   Label queries for monitoring, cost tracking, and debugging
   </details>

---

## 🚀 What You Can Do Now

✅ Configure Snowflake connections securely
✅ Understand cost implications of warehouses
✅ Set up key-based authentication
✅ Navigate Snowflake hierarchy (database → schema → table)
✅ Test connections before running expensive operations
✅ Apply security best practices

---

**Key Takeaway:** Cloud data warehouses like Snowflake fundamentally changed how we work with data. By separating compute and storage, they enable scalability and cost optimization impossible with traditional databases. You now understand both the "what" and the "why" of modern cloud data architecture.
