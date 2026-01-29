#!/usr/bin/env python3
"""
Deployment Verification Script
Tests both backend and dashboard services after Render deployment.
"""
import requests
import sys
import json
from urllib.parse import urlparse

def test_endpoint(url, description, expected_status=200):
    """Test an endpoint and return success status."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == expected_status:
            print(f"✅ {description}: OK ({response.status_code})")
            return True
        else:
            print(f"❌ {description}: Failed ({response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {description}: Error - {str(e)}")
        return False

def test_api_health(url):
    """Test API health endpoint and check Snowflake connection."""
    try:
        response = requests.get(f"{url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Health: OK")
            print(f"   Status: {data.get('status', 'unknown')}")
            if 'databases' in data:
                sf_status = data['databases'].get('snowflake', 'unknown')
                print(f"   Snowflake: {sf_status}")
            return True
        else:
            print(f"❌ API Health: Failed ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ API Health: Error - {str(e)}")
        return False

def main():
    """Main verification function."""
    print("=" * 70)
    print("Render Deployment Verification")
    print("=" * 70)
    print()
    
    # Get URLs from command line or use defaults
    if len(sys.argv) >= 3:
        api_url = sys.argv[1].rstrip('/')
        dashboard_url = sys.argv[2].rstrip('/')
    else:
        print("Usage: python verify_deployment.py <API_URL> <DASHBOARD_URL>")
        print()
        print("Example:")
        print("  python verify_deployment.py https://smartphone-intelligence-api.onrender.com https://smartphone-intelligence-dashboard.onrender.com")
        sys.exit(1)
    
    print(f"Backend API: {api_url}")
    print(f"Dashboard: {dashboard_url}")
    print()
    
    results = []
    
    # Test Backend
    print("Testing Backend API...")
    print("-" * 70)
    results.append(("Backend Root", test_endpoint(f"{api_url}/", "Backend Root Endpoint")))
    results.append(("Backend Health", test_api_health(api_url)))
    results.append(("Backend Docs", test_endpoint(f"{api_url}/docs", "API Documentation")))
    print()
    
    # Test Dashboard
    print("Testing Dashboard...")
    print("-" * 70)
    results.append(("Dashboard Health", test_endpoint(f"{dashboard_url}/_stcore/health", "Dashboard Health Check")))
    results.append(("Dashboard Main", test_endpoint(f"{dashboard_url}/", "Dashboard Main Page")))
    print()
    
    # Test API-Dashboard Connection
    print("Testing API-Dashboard Connection...")
    print("-" * 70)
    try:
        # Check if dashboard can reach API
        # This is a simple check - actual connection is tested in browser
        print(f"✅ Dashboard should connect to: {api_url}")
        print("   (Verify in browser: Check API status indicator)")
    except Exception as e:
        print(f"❌ Connection check failed: {str(e)}")
        results.append(("Connection", False))
    print()
    
    # Summary
    print("=" * 70)
    print("Verification Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print()
        print("🎉 All tests passed! Deployment is successful.")
        print()
        print("Next steps:")
        print(f"1. Open dashboard: {dashboard_url}")
        print("2. Verify API status shows 'Available'")
        print("3. Check charts load correctly")
        print("4. Verify no localhost references")
        return 0
    else:
        print()
        print("⚠️  Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
