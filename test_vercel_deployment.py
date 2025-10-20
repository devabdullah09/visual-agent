#!/usr/bin/env python3
"""
Test script to verify Vercel deployment compatibility
"""

import requests
import json
import time


def test_vercel_deployment():
    """Test the Vercel-compatible API"""
    print("🧪 Testing Vercel Deployment Compatibility")
    print("=" * 50)

    # Test data
    test_cases = [
        {
            "name": "Flowchart Test",
            "text": "Start\nUser visits website\nCheck if user is logged in?\nYes: Show dashboard\nNo: Show login page\nEnd",
            "type": "flowchart"
        },
        {
            "name": "Diagram Test",
            "text": "Frontend connects to API Gateway\nAPI Gateway routes to Auth Service\nAuth Service queries Database",
            "type": "diagram"
        },
        {
            "name": "Chart Test",
            "text": "Q1: 1000\nQ2: 1500\nQ3: 2000\nQ4: 1800",
            "type": "chart"
        }
    ]

    # Test local API (if running)
    try:
        print("🔍 Testing local API...")
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Local API is running")
            base_url = "http://localhost:5000"
        else:
            print("❌ Local API not responding")
            return
    except requests.exceptions.RequestException:
        print("❌ Local API not running. Start with: cd api && python index.py")
        return

    # Test each case
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📊 Test {i}: {test_case['name']}")

        try:
            # Test generate endpoint
            response = requests.post(
                f"{base_url}/generate",
                json={
                    "text": test_case["text"],
                    "type": test_case["type"]
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"  ✅ Generated {test_case['type']} successfully")
                    print(
                        f"  📏 HTML size: {len(data.get('html', ''))} characters")
                else:
                    print(
                        f"  ❌ Generation failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"  ❌ HTTP {response.status_code}: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"  ❌ Request failed: {e}")

    # Test web interface
    print(f"\n🌐 Testing web interface...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("  ✅ Web interface accessible")
            if "Visual Agent" in response.text:
                print("  ✅ Web interface content loaded correctly")
            else:
                print("  ⚠️  Web interface content may be incomplete")
        else:
            print(f"  ❌ Web interface failed: HTTP {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Web interface test failed: {e}")

    print(f"\n🎉 Vercel deployment test completed!")
    print(f"📝 Next steps:")
    print(f"  1. Push code to Git repository")
    print(f"  2. Deploy to Vercel using Vercel CLI or dashboard")
    print(f"  3. Test the deployed URL")


if __name__ == "__main__":
    test_vercel_deployment()
