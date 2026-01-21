"""
Test script to verify the server is working correctly
Run this after starting the server with: python main.py
"""
import requests
import json
import sys

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(text)
    print("="*60)

def test_server_running():
    """Test 1: Check if server is running"""
    print_header("TEST 1: Check if Server is Running")
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("[OK] Server is running!")
            print(f"   Message: {data.get('message', 'N/A')}")
            print(f"   Version: {data.get('version', 'N/A')}")
            return True
        else:
            print(f"[ERROR] Server returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to server!")
        print("   Make sure the server is running: python main.py")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_register():
    """Test 2: Register and get API key"""
    print_header("TEST 2: Register and Get API Key")
    try:
        registration_data = {
            "client_name": "Test Client",
            "email": "test@example.com",
            "purpose": "Server testing"
        }
        
        print("Sending registration request...")
        response = requests.post(
            "http://localhost:8000/register",
            json=registration_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            api_key = result.get('api_key')
            if api_key:
                print("[OK] Registration successful!")
                print(f"   API Key: {api_key[:30]}...")
                print(f"   Message: {result.get('message', 'N/A')}")
                return api_key
            else:
                print("[ERROR] No API key in response")
                return None
        else:
            print(f"[ERROR] Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

def test_api_key(api_key):
    """Test 3: Use API key to access endpoints"""
    print_header("TEST 3: Test API Key with Endpoints")
    
    if not api_key:
        print("[SKIP] No API key to test")
        return False
    
    headers = {"X-API-Key": api_key}
    tests_passed = 0
    tests_total = 0
    
    # Test 3a: Health check
    tests_total += 1
    try:
        response = requests.get("http://localhost:8000/health", headers=headers, timeout=5)
        if response.status_code == 200:
            print("[OK] Health check endpoint works")
            tests_passed += 1
        else:
            print(f"[FAIL] Health check failed: {response.status_code}")
    except Exception as e:
        print(f"[FAIL] Health check error: {e}")
    
    # Test 3b: Get tickers
    tests_total += 1
    try:
        response = requests.get("http://localhost:8000/tickers", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            tickers = data.get('tickers', [])
            count = data.get('count', 0)
            print(f"[OK] Tickers endpoint works")
            print(f"   Found {count} ticker(s): {tickers}")
            tests_passed += 1
        else:
            print(f"[FAIL] Tickers endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"[FAIL] Tickers endpoint error: {e}")
    
    # Test 3c: Get summary (if tickers exist)
    tests_total += 1
    try:
        response = requests.get("http://localhost:8000/tickers", headers=headers, timeout=5)
        if response.status_code == 200:
            tickers = response.json().get('tickers', [])
            if tickers:
                ticker = tickers[0]
                response = requests.get(
                    f"http://localhost:8000/data/{ticker}/summary",
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"[OK] Summary endpoint works for {ticker}")
                    print(f"   Total records: {data.get('total_records', 'N/A')}")
                    tests_passed += 1
                else:
                    print(f"[FAIL] Summary endpoint failed: {response.status_code}")
            else:
                print("[SKIP] No tickers available to test summary")
        else:
            print("[SKIP] Could not get tickers for summary test")
    except Exception as e:
        print(f"[FAIL] Summary endpoint error: {e}")
    
    print(f"\nResults: {tests_passed}/{tests_total} tests passed")
    return tests_passed == tests_total

def test_invalid_api_key():
    """Test 4: Verify invalid API key is rejected"""
    print_header("TEST 4: Test Invalid API Key Rejection")
    try:
        headers = {"X-API-Key": "invalid-key-12345"}
        response = requests.get("http://localhost:8000/tickers", headers=headers, timeout=5)
        if response.status_code == 403:
            print("[OK] Invalid API key correctly rejected")
            return True
        else:
            print(f"[WARNING] Invalid key returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("SERVER TEST SUITE")
    print("="*60)
    print("\nMake sure the server is running: python main.py")
    print("Then run this script in another terminal.\n")
    
    # Test 1: Server running
    if not test_server_running():
        print("\n[ABORT] Server is not running. Please start it first.")
        sys.exit(1)
    
    # Test 2: Register
    api_key = test_register()
    
    # Test 3: Use API key
    if api_key:
        test_api_key(api_key)
    
    # Test 4: Invalid key
    test_invalid_api_key()
    
    # Summary
    print_header("TEST SUMMARY")
    print("[OK] All critical tests completed!")
    print("\nIf all tests passed, your server is working correctly.")
    print("\nTo use the API:")
    print(f"  1. Your API key: {api_key[:30] + '...' if api_key else 'N/A'}")
    print("  2. Use it in X-API-Key header for all requests")
    print("  3. Example: headers = {'X-API-Key': 'your-key-here'}")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
