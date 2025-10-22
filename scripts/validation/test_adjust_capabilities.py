#!/usr/bin/env python3
"""
Adjust API Capability Validation Script

Tests Adjust API to validate:
1. Time granularity (hourly vs daily)
2. Available metrics and dimensions
3. Historical data depth
4. IAP revenue tracking capability
5. Cohort retention data availability
"""

import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv(dotenv_path=".secret/.env")


class AdjustCapabilityTester:
    """Test Adjust API capabilities"""

    def __init__(self):
        self.adjust_token = os.getenv("ADJUST_TOKEN", "")
        self.headers = {"Authorization": f"Bearer {self.adjust_token}"}
        self.base_url = "https://automate.adjust.com/reports-service/csv_report"

    def test_basic_connection(self):
        """Test basic Adjust API connection"""
        print("\n" + "=" * 70)
        print("TESTING ADJUST API CONNECTION")
        print("=" * 70)

        if not self.adjust_token:
            print("❌ ADJUST_TOKEN not found in environment")
            return False

        today = datetime.now().strftime("%Y-%m-%d")

        # Minimal test
        params = {
            "dimensions": "app",
            "metrics": "installs",
            "date_period": f"{today}:{today}",
            "utc_offset": "-04:00",
        }

        try:
            response = requests.get(self.base_url, headers=self.headers, params=params)

            if response.ok:
                print(f"✅ Connection successful (HTTP {response.status_code})")
                print(f"   Response size: {len(response.text)} bytes")
                return True
            else:
                print(f"❌ API error: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False

        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def test_available_dimensions(self):
        """Test different dimension combinations"""
        print("\n" + "=" * 70)
        print("TESTING ADJUST DIMENSIONS")
        print("=" * 70)

        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        dimension_tests = [
            {"name": "Basic (app only)", "dimensions": "app"},
            {"name": "App + Date", "dimensions": "app,day"},
            {
                "name": "App + Date + Country",
                "dimensions": "app,day,country_code,country",
            },
            {
                "name": "App + Date + Country + OS",
                "dimensions": "app,day,country_code,country,os_name",
            },
            {
                "name": "Full (with store_id)",
                "dimensions": "app,store_id,day,country_code,country,os_name",
            },
            {
                "name": "With Hour (time granularity)",
                "dimensions": "app,day,hour",  # Test if hourly data is available
            },
        ]

        for test in dimension_tests:
            print(f"\n📊 Testing: {test['name']}")
            print(f"   Dimensions: {test['dimensions']}")

            params = {
                "dimensions": test["dimensions"],
                "metrics": "installs",
                "date_period": f"{yesterday}:{yesterday}",
                "utc_offset": "-04:00",
            }

            try:
                response = requests.get(
                    self.base_url, headers=self.headers, params=params, timeout=30
                )

                if response.ok:
                    lines = response.text.strip().split("\n")
                    row_count = len(lines) - 1  # Exclude header
                    print(f"   ✅ SUCCESS - {row_count} rows returned")

                    # Show sample of first data row
                    if len(lines) > 1:
                        header = lines[0].split(",")
                        first_row = lines[1].split(",")
                        print(f"   Sample: {dict(zip(header[:5], first_row[:5]))}")

                else:
                    print(f"   ❌ FAILED - HTTP {response.status_code}")
                    print(f"   Error: {response.text[:200]}")

            except Exception as e:
                print(f"   ❌ FAILED - {str(e)[:100]}")

    def test_available_metrics(self):
        """Test different metric combinations"""
        print("\n" + "=" * 70)
        print("TESTING ADJUST METRICS")
        print("=" * 70)

        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        metric_tests = [
            {"name": "Basic (installs only)", "metrics": "installs"},
            {"name": "User Metrics", "metrics": "installs,daus"},
            {
                "name": "Revenue Metrics",
                "metrics": "ad_revenue,ad_impressions,ad_revenue_total_d0,ad_impressions_total_d0",
            },
            {"name": "Cost Metrics", "metrics": "network_cost,network_cost_diff"},
            {
                "name": "IAP Revenue (if available)",
                "metrics": "iap_revenue,revenue",  # Test if IAP revenue is tracked
            },
            {
                "name": "Retention Metrics (if available)",
                "metrics": "cohort_size_d0,cohort_size_d1,cohort_size_d7,cohort_size_d30",
            },
            {
                "name": "Complete Metrics Set",
                "metrics": "installs,daus,ad_revenue,ad_impressions,ad_revenue_total_d0,ad_impressions_total_d0,network_cost,network_cost_diff",
            },
        ]

        for test in metric_tests:
            print(f"\n📈 Testing: {test['name']}")
            print(f"   Metrics: {test['metrics']}")

            params = {
                "dimensions": "app,day",
                "metrics": test["metrics"],
                "date_period": f"{yesterday}:{yesterday}",
                "utc_offset": "-04:00",
            }

            try:
                response = requests.get(
                    self.base_url, headers=self.headers, params=params, timeout=30
                )

                if response.ok:
                    lines = response.text.strip().split("\n")
                    row_count = len(lines) - 1
                    print(f"   ✅ SUCCESS - {row_count} rows returned")

                    # Show what metrics are actually returned
                    if len(lines) > 0:
                        header = lines[0].split(",")
                        print(f"   Columns returned: {len(header)}")

                else:
                    print(f"   ❌ FAILED - HTTP {response.status_code}")
                    error_msg = response.text[:200]
                    if "Unknown metric" in error_msg:
                        print(f"   💡 Metric not available in this account")
                    else:
                        print(f"   Error: {error_msg}")

            except Exception as e:
                print(f"   ❌ FAILED - {str(e)[:100]}")

    def test_historical_depth(self):
        """Test how far back Adjust data is available"""
        print("\n" + "=" * 70)
        print("TESTING ADJUST HISTORICAL DATA DEPTH")
        print("=" * 70)

        test_ranges = [7, 30, 60, 90, 180, 365]

        for days_back in test_ranges:
            test_date = (datetime.now() - timedelta(days=days_back)).strftime(
                "%Y-%m-%d"
            )
            print(f"\n📅 Testing {days_back} days back ({test_date})")

            params = {
                "dimensions": "app,day",
                "metrics": "installs",
                "date_period": f"{test_date}:{test_date}",
                "utc_offset": "-04:00",
            }

            try:
                response = requests.get(
                    self.base_url, headers=self.headers, params=params, timeout=30
                )

                if response.ok:
                    lines = response.text.strip().split("\n")
                    row_count = len(lines) - 1
                    print(f"   ✅ Data available - {row_count} rows")
                else:
                    print(f"   ❌ No data or error: {response.text[:80]}")
                    break

            except Exception as e:
                print(f"   ❌ Error: {str(e)[:80]}")
                break

    def test_time_granularity(self):
        """Test if hourly data is available"""
        print("\n" + "=" * 70)
        print("TESTING TIME GRANULARITY (HOURLY DATA)")
        print("=" * 70)

        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        print(f"\n🕐 Testing hourly dimension for {yesterday}")

        params = {
            "dimensions": "app,day,hour",
            "metrics": "installs,daus",
            "date_period": f"{yesterday}:{yesterday}",
            "utc_offset": "-04:00",
        }

        try:
            response = requests.get(
                self.base_url, headers=self.headers, params=params, timeout=30
            )

            if response.ok:
                lines = response.text.strip().split("\n")
                row_count = len(lines) - 1
                print(f"   ✅ HOURLY DATA AVAILABLE - {row_count} rows returned")

                # Show sample with hour column
                if len(lines) > 1:
                    header = lines[0].split(",")
                    first_row = lines[1].split(",")
                    print(f"   Sample row: {dict(zip(header[:5], first_row[:5]))}")

                # Estimate hourly breakdown
                if row_count > 0:
                    print(f"\n   💡 Hourly granularity confirmed!")
                    print(f"   Expected: ~24 rows per app per day")
                    print(f"   Actual: {row_count} rows")

            else:
                print(f"   ❌ HOURLY DATA NOT AVAILABLE - HTTP {response.status_code}")
                print(f"   Error: {response.text[:200]}")
                print(f"\n   💡 Adjust likely only supports daily granularity")

        except Exception as e:
            print(f"   ❌ FAILED - {str(e)[:100]}")

    def print_summary(self):
        """Print summary of findings"""
        print("\n" + "=" * 70)
        print("ADJUST API VALIDATION SUMMARY")
        print("=" * 70)

        print("\n✅ RECOMMENDED CONFIGURATION FOR PROJECT:")
        print("   Dimensions: app, store_id, day, country_code, country, os_name")
        print(
            "   Metrics: installs, daus, ad_revenue, ad_impressions, ad_revenue_total_d0,"
        )
        print("            ad_impressions_total_d0, network_cost, network_cost_diff")
        print("   Time Granularity: Daily (hourly TBD)")
        print("   Historical Depth: TBD (test will confirm)")

        print("\n📋 NEXT STEPS:")
        print("   1. Run this script to confirm Adjust capabilities")
        print("   2. Compare with AdMob results (daily granularity confirmed)")
        print("   3. Update data_strategy.md with validated findings")
        print("   4. Finalize data model design based on confirmed dimensions")

    def run_all_tests(self):
        """Run all validation tests"""
        print("\n" + "=" * 70)
        print("ADJUST API CAPABILITY VALIDATION")
        print("Testing what data we can actually get from Adjust API")
        print("=" * 70)

        try:
            # Test 1: Basic connection
            if not self.test_basic_connection():
                print("\n❌ Cannot connect to Adjust API - stopping tests")
                return

            # Test 2: Dimensions
            self.test_available_dimensions()

            # Test 3: Metrics (including IAP revenue)
            self.test_available_metrics()

            # Test 4: Time granularity (hourly vs daily)
            self.test_time_granularity()

            # Test 5: Historical depth
            self.test_historical_depth()

            # Summary
            self.print_summary()

            print("\n✅ Adjust validation complete!")

        except KeyboardInterrupt:
            print("\n\n⚠️  Tests interrupted by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            raise


if __name__ == "__main__":
    tester = AdjustCapabilityTester()
    tester.run_all_tests()
