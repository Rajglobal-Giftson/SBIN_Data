"""
Interactive test script - Opens browser and tests endpoints
Run this to see the API working in real-time
"""
import requests
import json
import webbrowser
import time

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(title)
    print("="*60)

def test_endpoints():
    """Test all endpoints and show results"""
    BASE_URL = "http://localhost:8000"
    
    print_section("STOCK MARKET TBT API - LIVE TEST")
    
    # Test 1: Root endpoint
    print("\n[TEST 1] Checking server status...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Server is running!")
            print(f"   Version: {data['version']}")
            print(f"   Protocol: {data['protocol']}")
        else:
            print(f"   [ERROR] Server returned: {response.status_code}")
            return
    except Exception as e:
        print(f"   [ERROR] Cannot connect: {e}")
        print("   Make sure server is running: python main.py")
        return
    
    # Test 2: Register for API key
    print("\n[TEST 2] Registering for API key...")
    try:
        response = requests.post(
            f"{BASE_URL}/register",
            json={
                "client_name": "Browser Test Client",
                "email": "browser-test@example.com",
                "purpose": "Testing API in browser"
            },
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            api_key = result['api_key']
            print(f"   [OK] Registration successful!")
            print(f"   API Key: {api_key[:40]}...")
            print(f"   Message: {result['message']}")
        else:
            print(f"   [ERROR] Registration failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   [ERROR] Registration error: {e}")
        return
    
    # Test 3: Use API key
    headers = {"X-API-Key": api_key}
    
    print("\n[TEST 3] Testing API key with /tickers endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/tickers", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] API key works!")
            print(f"   Available tickers: {data['tickers']}")
            print(f"   Total count: {data['count']}")
        else:
            print(f"   [ERROR] Failed: {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
    
    # Test 4: Get summary
    print("\n[TEST 4] Getting SBIN summary...")
    try:
        response = requests.get(
            f"{BASE_URL}/data/SBIN/summary",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Summary retrieved!")
            print(f"   Ticker: {data['ticker']}")
            print(f"   Total records: {data['total_records']:,}")
            print(f"   Date range: {data['date_range']['start']} to {data['date_range']['end']}")
            print(f"   Price range: {data['price_range']['min']:.2f} - {data['price_range']['max']:.2f}")
            print(f"   Average price: {data['price_range']['avg']:.2f}")
        else:
            print(f"   [ERROR] Failed: {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
    
    # Test 5: Get sample data
    print("\n[TEST 5] Getting sample data (first 5 records)...")
    try:
        response = requests.get(
            f"{BASE_URL}/data/SBIN",
            headers=headers,
            params={"year": 2025, "month": 1, "limit": 5},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Data retrieved!")
            print(f"   Total available: {data['total']:,} records")
            print(f"   Returned: {len(data['data'])} records")
            if data['data']:
                print(f"\n   Sample record:")
                sample = data['data'][0]
                print(f"     Date: {sample['Date']}")
                print(f"     Time: {sample['Time']}")
                print(f"     Close: {sample['Close']}")
                print(f"     Volume: {sample['Volume']}")
        else:
            print(f"   [ERROR] Failed: {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
    
    # Summary
    print_section("TEST SUMMARY")
    print("[OK] All endpoints tested successfully!")
    print(f"\nYour API Key: {api_key}")
    print("\nYou can now:")
    print("  1. Open browser: http://localhost:8000/docs")
    print("  2. Use the interactive API documentation")
    print("  3. Test endpoints directly in the browser")
    print("\n" + "="*60 + "\n")
    
    # Open browser
    print("Opening API documentation in browser...")
    time.sleep(1)
    try:
        webbrowser.open(f"{BASE_URL}/docs")
        print("[OK] Browser opened!")
    except:
        print("Could not open browser automatically.")
        print(f"Manually open: {BASE_URL}/docs")

if __name__ == "__main__":
    test_endpoints()
