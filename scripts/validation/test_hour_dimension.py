#!/usr/bin/env python3
"""
Focused test for HOUR dimension in AdMob API

Based on Google documentation:
- HOUR dimension supported in both networkReport and mediationReport
- DATE dimension MUST be included with HOUR
- Maximum 28 days when using HOUR
- Start date cannot be > 28 days in the past
"""

import os
import pickle
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json


def authenticate_admob(publisher_id):
    """Authenticate with AdMob"""
    token_file = f"./.secret/token_{publisher_id}.pickle"

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
        print(f"❌ Auth failed: {e}")
        return None


def test_hour_dimension_variations():
    """Test different variations of HOUR dimension requests"""

    publisher_id = "pub-3717786786472633"
    service = authenticate_admob(publisher_id)

    if not service:
        return

    print("\n" + "="*70)
    print("TESTING HOUR DIMENSION - Multiple Strategies")
    print("="*70)

    # Use yesterday (2 days ago to avoid incomplete data)
    test_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    date_obj = datetime.strptime(test_date, "%Y-%m-%d").date()

    print(f"\nTest date: {test_date} (2 days ago to avoid incomplete data)")

    # Test cases to try
    test_cases = [
        {
            "name": "Network Report - HOUR + DATE (minimal)",
            "api": "networkReport",
            "dimensions": ["DATE", "HOUR"],
            "metrics": ["ESTIMATED_EARNINGS"]
        },
        {
            "name": "Network Report - HOUR + DATE + APP",
            "api": "networkReport",
            "dimensions": ["DATE", "HOUR", "APP"],
            "metrics": ["ESTIMATED_EARNINGS", "IMPRESSIONS"]
        },
        {
            "name": "Network Report - Full dimensions with HOUR",
            "api": "networkReport",
            "dimensions": ["DATE", "HOUR", "APP", "COUNTRY", "PLATFORM"],
            "metrics": ["ESTIMATED_EARNINGS", "IMPRESSIONS"]
        },
        {
            "name": "Mediation Report - HOUR + DATE (minimal)",
            "api": "mediationReport",
            "dimensions": ["DATE", "HOUR"],
            "metrics": ["ESTIMATED_EARNINGS"]
        },
        {
            "name": "Mediation Report - HOUR + DATE + APP",
            "api": "mediationReport",
            "dimensions": ["DATE", "HOUR", "APP"],
            "metrics": ["ESTIMATED_EARNINGS", "IMPRESSIONS"]
        },
        {
            "name": "Mediation Report - Full dimensions with HOUR",
            "api": "mediationReport",
            "dimensions": ["DATE", "HOUR", "APP", "COUNTRY", "PLATFORM"],
            "metrics": ["ESTIMATED_EARNINGS", "IMPRESSIONS"]
        },
    ]

    for test in test_cases:
        print(f"\n{'='*70}")
        print(f"TEST: {test['name']}")
        print(f"API: {test['api']}")
        print(f"Dimensions: {test['dimensions']}")
        print(f"Metrics: {test['metrics']}")
        print(f"{'='*70}")

        try:
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

            print(f"\nRequest spec:")
            print(json.dumps(report_spec, indent=2))

            # Call appropriate API
            if test["api"] == "networkReport":
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

            # Count rows
            row_count = 0
            if isinstance(response, list):
                for item in response:
                    if item.get("row"):
                        row_count += 1
                        # Print first row for inspection
                        if row_count == 1:
                            print(f"\n✅ SUCCESS! First row sample:")
                            row_data = item.get("row", {})
                            print(f"   Dimensions: {row_data.get('dimensionValues', {})}")
                            print(f"   Metrics: {row_data.get('metricValues', {})}")

            print(f"\n✅ TOTAL ROWS: {row_count}")

            if row_count > 0:
                print(f"\n🎉 HOUR DIMENSION WORKS WITH THIS CONFIGURATION!")
                print(f"   API: {test['api']}")
                print(f"   Dimensions: {test['dimensions']}")
                return  # Stop testing, we found a working config

        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ FAILED")
            print(f"   Error: {error_msg}")

            # Try to extract more details from error
            if "400" in error_msg:
                print(f"\n   💡 HTTP 400 = Bad Request")
                print(f"   Possible causes:")
                print(f"   - Dimension not supported by this API type")
                print(f"   - Invalid dimension combination")
                print(f"   - Date range issue (must be within 28 days)")
            elif "403" in error_msg:
                print(f"\n   💡 HTTP 403 = Permission denied")
                print(f"   - Your account may not have access to this API endpoint")

    print("\n" + "="*70)
    print("CONCLUSION")
    print("="*70)
    print("❌ HOUR dimension failed in all tested configurations")
    print("\nPossible reasons:")
    print("1. Your AdMob account may not have HOUR dimension enabled")
    print("2. HOUR dimension may only be available in certain regions/tiers")
    print("3. HOUR dimension may require special API access or permissions")
    print("4. The feature may be in beta/alpha and not generally available")
    print("\nRecommendation: Proceed with DAILY granularity only")


if __name__ == "__main__":
    test_hour_dimension_variations()
