"""
All-in-one script: Start server, wait, register, and get API key
"""
import subprocess
import sys
import time
import requests
import json
from pathlib import Path

def start_server():
    """Start the server process"""
    print("Starting server...")
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=Path(__file__).parent,
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
    )
    return process

def wait_for_server(max_wait=20):
    """Wait for server to be ready"""
    print("Waiting for server to start...")
    for i in range(max_wait):
        try:
            response = requests.get("http://localhost:8000/", timeout=2)
            if response.status_code == 200:
                print("[OK] Server is ready!")
                return True
        except:
            pass
        time.sleep(1)
        if i % 3 == 0 and i > 0:
            print(f"  Still waiting... ({i}/{max_wait})")
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
    
    print(f"\nRegistration info:")
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
            api_key = result['api_key']
            print(f"\n{api_key}\n")
            print("="*60)
            print("\n[IMPORTANT] Save this key immediately!")
            print("It will NOT be shown again.\n")
            
            # Save to file
            key_file = Path("my_api_key.txt")
            with open(key_file, 'w') as f:
                f.write(api_key)
            print(f"[OK] API key saved to: {key_file.absolute()}")
            
            # Test the API key
            print("\nTesting API key...")
            test_api_key(api_key)
            
            return api_key
        else:
            print(f"\n[ERROR] Registration failed: {response.status_code}")
            print(response.text)
            return None
            
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Cannot connect to server!")
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
            return True
        else:
            print(f"[WARNING] API key test returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"[WARNING] Could not test API key: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("AUTOMATIC SERVER START & API KEY REGISTRATION")
    print("="*60)
    
    # Check if server is already running
    try:
        response = requests.get("http://localhost:8000/", timeout=2)
        print("[OK] Server is already running!")
        server_running = True
    except:
        server_running = False
        # Start server
        print("\nStep 1: Starting server...")
        process = start_server()
        print("[OK] Server process started")
        print("Note: Server is running in a separate window")
        print("      Keep that window open while using the API")
        
        # Wait for server
        if not wait_for_server():
            print("\n[ERROR] Server did not start in time.")
            print("Please check for errors and try again.")
            sys.exit(1)
    
    # Register and get key
    print("\nStep 2: Registering to get API key...")
    api_key = register_and_get_key()
    
    if api_key:
        print("\n" + "="*60)
        print("COMPLETE!")
        print("="*60)
        print(f"\nYour API Key: {api_key}")
        print(f"\nSaved to: my_api_key.txt")
        print("\nUse this key in the X-API-Key header for all requests.")
        print("\nExample Python code:")
        print("  import requests")
        print("  headers = {'X-API-Key': '" + api_key[:30] + "...'}")
        print("  response = requests.get('http://localhost:8000/tickers', headers=headers)")
        print("\n" + "="*60 + "\n")
        
        if not server_running:
            print("[NOTE] The server is running in a separate window.")
            print("       Keep it running to use the API.")
            print("       Close it when you're done.\n")
    else:
        print("\n[ERROR] Failed to get API key. Please try again.\n")
        sys.exit(1)
