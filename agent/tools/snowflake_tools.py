"""
Snowflake query tool for AI Agent.

Enables natural language → SQL → results flow.
"""

import sys
from pathlib import Path
from typing import Annotated

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from langchain_core.tools import tool
from scripts.utils.snowflake_client import get_snowflake_client


# Tool documentation for LLM
SCHEMA_CONTEXT = """
## Available Tables (DB_T34.ANALYTICS schema)

### fct_app_daily_performance (Main fact table)
Grain: One row per app × date × country × platform

Columns:
- performance_key: Surrogate key
- app_key: FK to dim_apps
- date_key: FK to dim_dates
- country_code: Country (e.g., 'US', 'TH', 'VN')
- platform: 'IOS' or 'ANDROID'

Revenue (AdMob - source of truth):
- ad_revenue: Daily ad revenue in USD
- ad_impressions: Ad impressions count
- ad_clicks: Ad clicks count

Cohort metrics (for LTV analysis):
- ad_revenue_d0: Day 0 revenue (install day, ~70-80% of LTV)
- ad_revenue_d1: Cumulative revenue through day 1
- ad_revenue_d3: Cumulative revenue through day 3
- ad_revenue_d7: Cumulative revenue through day 7 (~95% of LTV)
- ad_impressions_d0, ad_impressions_d1, ad_impressions_d3, ad_impressions_d7

Cost & Users:
- network_cost: UA spend (cost to acquire users)
- installs: New user installs
- daus: Daily active users
- paid_impressions: UA ad impressions

IAP:
- subscrevnt_revenue: In-app purchase revenue

For reconciliation:
- ad_revenue_adjust: Adjust's revenue estimate (compare with ad_revenue)

### dim_apps
- app_key: Surrogate key (join with fct)
- app_store_id: Package ID
- app_name: Display name

### dim_dates
- date_key: Surrogate key (join with fct)
- date: Actual date
- year, month, day
- day_of_week, day_name

## Common Metric Formulas

```sql
-- ROAS (Return on Ad Spend) - profitability indicator
d0_roas = SUM(ad_revenue_d0) / NULLIF(SUM(network_cost), 0) * 100
d7_roas = SUM(ad_revenue_d7) / NULLIF(SUM(network_cost), 0) * 100

-- CPI (Cost Per Install) - acquisition cost
cpi = SUM(network_cost) / NULLIF(SUM(installs), 0)

-- eCPM (Revenue per 1000 impressions) - monetization
ecpm = SUM(ad_revenue) * 1000 / NULLIF(SUM(ad_impressions), 0)

-- IMPDAU (Impressions per DAU) - engagement
impdau = SUM(ad_impressions) / NULLIF(SUM(daus), 0)
```

## IMPORTANT: ROAS Queries
When calculating ROAS, many apps have NULL (no cost data). To show meaningful results:
1. Filter: HAVING SUM(network_cost) > 0
2. Sort: ORDER BY d0_roas DESC NULLS LAST
Example:
```sql
SELECT a.app_name,
       ROUND(SUM(f.ad_revenue_d0) / NULLIF(SUM(f.network_cost), 0) * 100, 1) as d0_roas
FROM fct_app_daily_performance f
JOIN dim_apps a ON f.app_key = a.app_key
GROUP BY a.app_name
HAVING SUM(f.network_cost) > 0
ORDER BY d0_roas DESC
LIMIT 10
```

## Data Context
- Date range: Dec 25, 2025 to present (updated daily)
- Apps: 59 apps
- Countries: 240 countries
- Use MAX(date) FROM dim_dates to get the latest date
"""


@tool
def query_snowflake(sql_query: Annotated[str, "Valid Snowflake SQL query"]) -> str:
    """
    Execute a SQL query against Snowflake analytics tables.

    Use this tool to query mobile app performance data including:
    - Revenue metrics (ad_revenue, ad_revenue_d0 through d7)
    - Cost metrics (network_cost, cpi)
    - User metrics (installs, daus)
    - App and country breakdowns

    Always use the ANALYTICS schema (it's the default).
    Join with dim_apps for app names and dim_dates for date filtering.

    Example queries:
    - Total revenue: SELECT SUM(ad_revenue) FROM fct_app_daily_performance
    - By app: SELECT a.app_name, SUM(f.ad_revenue) FROM fct_app_daily_performance f JOIN dim_apps a ON f.app_key = a.app_key GROUP BY a.app_name
    - ROAS: SELECT SUM(ad_revenue_d0) / NULLIF(SUM(network_cost), 0) as d0_roas FROM fct_app_daily_performance

    Args:
        sql_query: A valid Snowflake SQL query

    Returns:
        Query results as formatted text, or error message if query fails
    """
    try:
        # Connect to Snowflake ANALYTICS schema
        client = get_snowflake_client(schema="ANALYTICS")

        try:
            # Execute query
            df = client.execute_query(sql_query)

            if df.empty:
                return "Query returned no results."

            # Format results
            # Limit to 50 rows for readability
            if len(df) > 50:
                result = f"Showing first 50 of {len(df)} rows:\n\n"
                result += df.head(50).to_string(index=False)
            else:
                result = f"Results ({len(df)} rows):\n\n"
                result += df.to_string(index=False)

            return result

        finally:
            client.close()

    except Exception as e:
        return f"Query error: {str(e)}\n\nPlease check your SQL syntax and table/column names."


def get_schema_context() -> str:
    """Return schema documentation for system prompt."""
    return SCHEMA_CONTEXT


# Test function
if __name__ == "__main__":
    print("Testing Snowflake tool...\n")

    # Test 1: Simple count
    print("Test 1: Row count")
    result = query_snowflake.invoke("SELECT COUNT(*) as total_rows FROM fct_app_daily_performance")
    print(result)
    print()

    # Test 2: Top apps by revenue
    print("Test 2: Top 5 apps by revenue")
    result = query_snowflake.invoke("""
        SELECT a.app_name, ROUND(SUM(f.ad_revenue), 2) as revenue
        FROM fct_app_daily_performance f
        JOIN dim_apps a ON f.app_key = a.app_key
        GROUP BY a.app_name
        ORDER BY revenue DESC
        LIMIT 5
    """)
    print(result)
    print()

    # Test 3: ROAS calculation
    print("Test 3: Overall D0 ROAS")
    result = query_snowflake.invoke("""
        SELECT
            ROUND(SUM(ad_revenue_d0), 2) as total_d0_revenue,
            ROUND(SUM(network_cost), 2) as total_cost,
            ROUND(SUM(ad_revenue_d0) / NULLIF(SUM(network_cost), 0) * 100, 1) as d0_roas_pct
        FROM fct_app_daily_performance
    """)
    print(result)
