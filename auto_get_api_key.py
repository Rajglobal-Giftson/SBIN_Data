"""
Automatically register and get API key (non-interactive)
"""
import requests
import json
import time

def wait_for_server(max_wait=15):
    """Wait for server to be ready"""
    print("Waiting for server to start...")
    for i in range(max_wait):
        try:
            response = requests.get("http://localhost:8000/", timeout=2)
            if response.status_code == 200:
                print("[OK] Server is ready!")
                return True
        except:
            time.sleep(1)
            if i % 3 == 0:
                print(f"  Waiting... ({i+1}/{max_wait})")
    return False

def register_and_get_key():
    """Register and get API key"""
    print("\n" + "="*60)
    print("REGISTERING TO GET API KEY")
    print("="*60)
    
    registration_data = {
        'client_name': 'API Client',
        'email': 'client@example.com',
        'purpose': 'Stock market data access'
    }
    
    print(f"\nRegistration data:")
    print(f"  Name: {registration_data['client_name']}")
    print(f"  Email: {registration_data['email']}")
    print(f"  Purpose: {registration_data['purpose']}")
    print("\nSending registration request...")
    
    try:
        response = requests.post(
            'http://localhost:8000/register',
            json=registration_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n" + "="*60)
            print("SUCCESS! YOUR API KEY:")
            print("="*60)
            print(f"\n{result['api_key']}\n")
            print("="*60)
            print("\n[IMPORTANT] Save this key immediately!")
            print("It will NOT be shown again.\n")
            
            # Test the API key
            print("Testing API key...")
            test_api_key(result['api_key'])
            
            return result['api_key']
        else:
            print(f"\n[ERROR] Registration failed: {response.status_code}")
            print(response.text)
            return None
            
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Cannot connect to server!")
        print("Make sure the server is running: python main.py")
        return None
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return None

def test_api_key(api_key):
    """Test the API key"""
    headers = {"X-API-Key": api_key}
    
    try:
        response = requests.get(
            "http://localhost:8000/tickers",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print("[OK] API key works!")
            print(f"Available tickers: {result.get('tickers', [])}")
            print(f"Total: {result.get('count', 0)} ticker(s)")
        else:
            print(f"[WARNING] API key test returned: {response.status_code}")
    except Exception as e:
        print(f"[WARNING] Could not test API key: {e}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("AUTOMATIC API KEY REGISTRATION")
    print("="*60)
    
    # Wait for server
    if not wait_for_server():
        print("\n[ERROR] Server did not start in time.")
        print("Please start the server manually: python main.py")
        exit(1)
    
    # Register and get key
    api_key = register_and_get_key()
    
    if api_key:
        print("\n" + "="*60)
        print("REGISTRATION COMPLETE!")
        print("="*60)
        print(f"\nYour API Key: {api_key}")
        print("\nUse this key in the X-API-Key header for all requests.")
        print("Example:")
        print("  headers = {'X-API-Key': '" + api_key[:20] + "...'}")
        print("\n" + "="*60 + "\n")
    else:
        print("\n[ERROR] Failed to get API key. Please try again.\n")
