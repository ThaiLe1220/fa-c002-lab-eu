# Creating Sample Data in Snowflake

## Step 1: Run this SQL in Snowflake Worksheets

Copy and paste this into your Snowflake web interface:

```sql
-- Create a simple RAW schema for source data
CREATE SCHEMA IF NOT EXISTS DB_T34.RAW;

-- Create a simple customers table
CREATE OR REPLACE TABLE DB_T34.RAW.CUSTOMERS (
    customer_id INT,
    customer_name VARCHAR(100),
    email VARCHAR(100),
    city VARCHAR(50),
    signup_date DATE,
    total_orders INT,
    total_spent DECIMAL(10,2)
);

-- Insert sample data
INSERT INTO DB_T34.RAW.CUSTOMERS VALUES
    (1, 'John Doe', 'john@example.com', 'New York', '2024-01-15', 5, 299.99),
    (2, 'Jane Smith', 'jane@example.com', 'Los Angeles', '2024-02-20', 3, 150.50),
    (3, 'Bob Johnson', 'bob@example.com', 'Chicago', '2024-03-10', 8, 450.00),
    (4, 'Alice Williams', 'alice@example.com', 'Houston', '2024-01-25', 12, 899.99),
    (5, 'Charlie Brown', 'charlie@example.com', 'Phoenix', '2024-04-05', 2, 75.25),
    (6, 'Diana Prince', 'diana@example.com', 'Philadelphia', '2024-02-14', 6, 320.00),
    (7, 'Eve Davis', 'eve@example.com', 'San Antonio', '2024-03-22', 4, 200.00),
    (8, 'Frank Miller', 'frank@example.com', 'San Diego', '2024-01-30', 10, 650.75),
    (9, 'Grace Lee', 'grace@example.com', 'Dallas', '2024-04-12', 1, 49.99),
    (10, 'Henry Ford', 'henry@example.com', 'Austin', '2024-02-28', 7, 380.50);

-- Verify data
SELECT * FROM DB_T34.RAW.CUSTOMERS;
SELECT COUNT(*) FROM DB_T34.RAW.CUSTOMERS;
```

## Step 2: Verify in Snowflake

You should see:
- ✅ Schema `RAW` created
- ✅ Table `CUSTOMERS` created
- ✅ 10 rows inserted

---

## What We Created

**Simple customer data with:**
- `customer_id` - Unique ID
- `customer_name` - Full name
- `email` - Email address
- `city` - Location
- `signup_date` - When they joined
- `total_orders` - Number of orders
- `total_spent` - Total money spent

**This is our "raw" data that dbt will transform!**
