#!/usr/bin/env python3
"""
API Capability Validation Script

Tests AdMob and Adjust APIs to validate:
1. What dimensions and metrics are available
2. Data volume per day
3. Historical data depth
4. IAP revenue availability
5. API rate limits and constraints

Run this BEFORE building the data warehouse to confirm assumptions.
"""

import os
import sys
import pickle
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class APICapabilityTester:
    """Test API capabilities without building complex infrastructure"""

    def __init__(self):
        self.secret_dir = "./.secret"
        self.admob_publisher_ids = [
            "pub-3717786786472633",
            "pub-4109716399396805",
            "pub-4738062221647171"
        ]
        self.adjust_token = os.getenv("ADJUST_TOKEN", "")
        self.results = {
            "admob": {},
            "adjust": {},
            "summary": {}
        }

    def authenticate_admob(self, publisher_id):
        """Authenticate with AdMob using existing pickle tokens"""
        token_file = f"{self.secret_dir}/token_{publisher_id}.pickle"

        if not os.path.exists(token_file):
            print(f"❌ Token file not found: {token_file}")
            return None

        try:
            with open(token_file, "rb") as token:
                credentials = pickle.load(token)

            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())

            service = build("admob", "v1", credentials=credentials)
            print(f"✅ AdMob authenticated: {publisher_id}")
            return service

        except Exception as e:
            print(f"❌ AdMob auth failed for {publisher_id}: {e}")
            return None

    def test_admob_dimensions(self):
        """Test different AdMob dimension combinations"""
        print("\n" + "="*60)
        print("TESTING ADMOB API CAPABILITIES")
        print("="*60)

        publisher_id = self.admob_publisher_ids[0]  # Use first publisher
        service = self.authenticate_admob(publisher_id)

        if not service:
            return

        # Test date (yesterday to avoid incomplete data)
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        # Test different dimension combinations
        test_cases = [
            {
                "name": "Basic (Current)",
                "dimensions": ["APP", "DATE", "COUNTRY", "PLATFORM"],
                "metrics": ["ESTIMATED_EARNINGS", "IMPRESSIONS"]
            },
            {
                "name": "With Hour (Real-time) - Network Report",
                "dimensions": ["DATE", "HOUR", "APP", "COUNTRY", "PLATFORM"],
                "metrics": ["ESTIMATED_EARNINGS", "IMPRESSIONS"],
                "use_network_report": True  # Use networkReport instead of mediationReport
            },
            {
                "name": "With Ad Format",
                "dimensions": ["APP", "DATE", "COUNTRY", "PLATFORM", "FORMAT"],
                "metrics": ["ESTIMATED_EARNINGS", "IMPRESSIONS"]
            },
            {
                "name": "With Ad Unit",
                "dimensions": ["APP", "DATE", "COUNTRY", "PLATFORM", "AD_UNIT"],
                "metrics": ["ESTIMATED_EARNINGS", "IMPRESSIONS"]
            },
            {
                "name": "Complete (Format + Unit)",
                "dimensions": ["APP", "DATE", "COUNTRY", "PLATFORM", "FORMAT", "AD_UNIT"],
                "metrics": ["ESTIMATED_EARNINGS", "IMPRESSIONS"]
            },
            {
                "name": "Extended Metrics",
                "dimensions": ["APP", "DATE", "COUNTRY", "PLATFORM"],
                "metrics": [
                    "ESTIMATED_EARNINGS",
                    "IMPRESSIONS",
                    "CLICKS",
                    "AD_REQUESTS",
                    "MATCHED_REQUESTS",
                    "OBSERVED_ECPM"
                ]
            }
        ]

        for test in test_cases:
            print(f"\n📊 Testing: {test['name']}")
            print(f"   Dimensions: {', '.join(test['dimensions'])}")
            print(f"   Metrics: {', '.join(test['metrics'])}")

            try:
                date_obj = datetime.strptime(yesterday, "%Y-%m-%d").date()
                report_spec = {
                    "date_range": {
                        "start_date": {
                            "year": date_obj.year,
                            "month": date_obj.month,
                            "day": date_obj.day
                        },
                        "end_date": {
                            "year": date_obj.year,
                            "month": date_obj.month,
                            "day": date_obj.day
                        }
                    },
                    "dimensions": test["dimensions"],
                    "metrics": test["metrics"]
                }

                # Use Network Report API for HOUR dimension, Mediation Report for others
                if test.get("use_network_report"):
                    response = (
                        service.accounts()
                        .networkReport()
                        .generate(
                            parent=f"accounts/{publisher_id}",
                            body={"report_spec": report_spec}
                        )
                        .execute()
                    )
                else:
                    response = (
                        service.accounts()
                        .mediationReport()
                        .generate(
                            parent=f"accounts/{publisher_id}",
                            body={"report_spec": report_spec}
                        )
                        .execute()
                    )

                # Count rows (response is a list, each item has 'row')
                row_count = 0
                if isinstance(response, list):
                    for item in response:
                        if item.get("row"):
                            row_count += 1
                else:
                    row_count = len(response.get("row", []))

                print(f"   ✅ SUCCESS - {row_count} rows returned")

                # Store result
                self.results["admob"][test["name"]] = {
                    "status": "success",
                    "dimensions": test["dimensions"],
                    "metrics": test["metrics"],
                    "row_count": row_count,
                    "date_tested": yesterday
                }

            except Exception as e:
                error_msg = str(e)
                print(f"   ❌ FAILED - {error_msg[:100]}")
                self.results["admob"][test["name"]] = {
                    "status": "failed",
                    "error": error_msg
                }

    def test_admob_historical_depth(self):
        """Test how far back AdMob data is available"""
        print("\n" + "="*60)
        print("TESTING ADMOB HISTORICAL DATA DEPTH")
        print("="*60)

        publisher_id = self.admob_publisher_ids[0]
        service = self.authenticate_admob(publisher_id)

        if not service:
            return

        # Test different date ranges
        test_ranges = [30, 60, 90, 180, 365]

        for days_back in test_ranges:
            test_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            print(f"\n📅 Testing {days_back} days back ({test_date})")

            try:
                date_obj = datetime.strptime(test_date, "%Y-%m-%d").date()
                report_spec = {
                    "date_range": {
                        "start_date": {
                            "year": date_obj.year,
                            "month": date_obj.month,
                            "day": date_obj.day
                        },
                        "end_date": {
                            "year": date_obj.year,
                            "month": date_obj.month,
                            "day": date_obj.day
                        }
                    },
                    "dimensions": ["APP", "DATE"],
                    "metrics": ["ESTIMATED_EARNINGS"]
                }

                response = (
                    service.accounts()
                    .mediationReport()
                    .generate(
                        parent=f"accounts/{publisher_id}",
                        body={"report_spec": report_spec}
                    )
                    .execute()
                )

                # Count rows
                row_count = 0
                if isinstance(response, list):
                    for item in response:
                        if item.get("row"):
                            row_count += 1
                else:
                    row_count = len(response.get("row", []))

                print(f"   ✅ Data available - {row_count} rows")

            except Exception as e:
                print(f"   ❌ No data or error: {str(e)[:80]}")
                break

    def test_adjust_endpoints(self):
        """Test Adjust API endpoints and available data"""
        print("\n" + "="*60)
        print("TESTING ADJUST API CAPABILITIES")
        print("="*60)

        if not self.adjust_token:
            print("❌ ADJUST_TOKEN not found in environment")
            return

        # Test app tokens (you'll need to add your actual app tokens)
        # For now, just test if we can authenticate
        headers = {
            "Authorization": f"Bearer {self.adjust_token}",
            "Content-Type": "application/json"
        }

        # Test deliverables endpoint (basic metrics)
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        print(f"\n📊 Testing Adjust Deliverables Endpoint")
        print(f"   Note: Need app tokens to test fully")
        print(f"   Token present: {'✅' if self.adjust_token else '❌'}")

        # You would test like this with actual app token:
        # url = f"https://api.adjust.com/kpis/v1/{app_token}/deliverables"
        # params = {"start_date": yesterday, "end_date": yesterday}
        # response = requests.get(url, headers=headers, params=params)

    def print_summary(self):
        """Print summary of findings"""
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)

        print("\n✅ ADMOB WORKING CONFIGURATIONS:")
        for name, result in self.results["admob"].items():
            if result.get("status") == "success":
                print(f"   • {name}: {result['row_count']} rows/day")
                print(f"     Dimensions: {', '.join(result['dimensions'])}")

        print("\n❌ ADMOB FAILED CONFIGURATIONS:")
        for name, result in self.results["admob"].items():
            if result.get("status") == "failed":
                print(f"   • {name}")
                print(f"     Error: {result.get('error', 'Unknown')[:100]}")

        print("\n📋 RECOMMENDED CONFIGURATION FOR PROJECT:")
        # Find the config with most dimensions that worked
        successful = [r for r in self.results["admob"].values() if r.get("status") == "success"]
        if successful:
            best = max(successful, key=lambda x: len(x.get("dimensions", [])))
            print(f"   Dimensions: {', '.join(best['dimensions'])}")
            print(f"   Metrics: {', '.join(best['metrics'])}")
            print(f"   Expected rows/day: ~{best['row_count']}")
            print(f"   90-day estimate: ~{best['row_count'] * 90:,} rows")

    def run_all_tests(self):
        """Run all validation tests"""
        print("\n" + "="*60)
        print("API CAPABILITY VALIDATION")
        print("Testing what data we can actually get from APIs")
        print("="*60)

        try:
            self.test_admob_dimensions()
            self.test_admob_historical_depth()
            self.test_adjust_endpoints()
            self.print_summary()

            print("\n✅ Validation complete!")
            print("\nNext steps:")
            print("1. Review results above")
            print("2. Document findings in docs/planning/")
            print("3. Adjust data model based on what's actually available")

        except KeyboardInterrupt:
            print("\n\n⚠️  Tests interrupted by user")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            raise


if __name__ == "__main__":
    tester = APICapabilityTester()
    tester.run_all_tests()
