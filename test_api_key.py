"""
Test script to demonstrate how to get an API key
"""
import requests
import json
import time
import subprocess
import sys
from pathlib import Path

def start_server():
    """Start the server in background"""
    print("Starting server...")
    # Start server in background
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=Path(__file__).parent
    )
    return process

def wait_for_server(max_wait=10):
    """Wait for server to be ready"""
    print("Waiting for server to start...")
    for i in range(max_wait):
        try:
            response = requests.get("http://localhost:8000/", timeout=2)
            if response.status_code == 200:
                print("✓ Server is ready!")
                return True
        except:
            time.sleep(1)
            print(f"  Waiting... ({i+1}/{max_wait})")
    return False

def register_client():
    """Register a client and get API key"""
    print("\n" + "="*60)
    print("STEP 1: Register to get an API key")
    print("="*60)
    
    registration_data = {
        "client_name": "Test Client",
        "email": "test@example.com",
        "purpose": "Testing API key registration"
    }
    
    print(f"\nSending registration request...")
    print(f"URL: http://localhost:8000/register")
    print(f"Data: {json.dumps(registration_data, indent=2)}")
    
    try:
        response = requests.post(
            "http://localhost:8000/register",
            json=registration_data,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n[SUCCESS] Registration successful!")
            print(f"\n{'='*60}")
            print("YOUR API KEY:")
            print("="*60)
            print(f"\n{result['api_key']}\n")
            print("="*60)
            print(f"\n[WARNING] IMPORTANT: Save this API key immediately!")
            print(f"   It will NOT be shown again.\n")
            print(f"Message: {result['message']}")
            return result['api_key']
        else:
            print(f"[ERROR] Error: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"[ERROR] Error connecting to server: {e}")
        return None

def test_api_key(api_key):
    """Test the API key by making a request"""
    if not api_key:
        return
    
    print("\n" + "="*60)
    print("STEP 2: Test your API key")
    print("="*60)
    
    headers = {"X-API-Key": api_key}
    
    print(f"\nTesting API key with /tickers endpoint...")
    print(f"URL: http://localhost:8000/tickers")
    print(f"Header: X-API-Key: {api_key[:20]}...")
    
    try:
        response = requests.get(
            "http://localhost:8000/tickers",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n[SUCCESS] API key works!")
            print(f"\nAvailable tickers: {result.get('tickers', [])}")
            print(f"Total tickers: {result.get('count', 0)}")
        else:
            print(f"[ERROR] Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"[ERROR] Error: {e}")

def show_instructions():
    """Show instructions for getting API key"""
    print("\n" + "="*60)
    print("HOW TO GET AN API KEY - INSTRUCTIONS")
    print("="*60)
    print("""
Method 1: Using Python (requests library)
------------------------------------------
import requests

response = requests.post(
    'http://localhost:8000/register',
    json={
        'client_name': 'Your Name',
        'email': 'your@email.com',
        'purpose': 'What you will use it for'
    }
)

api_key = response.json()['api_key']
print(f"Your API Key: {api_key}")

Method 2: Using cURL (Command Line)
------------------------------------
curl -X POST http://localhost:8000/register \\
  -H "Content-Type: application/json" \\
  -d '{
    "client_name": "Your Name",
    "email": "your@email.com",
    "purpose": "What you will use it for"
  }'

Method 3: Using PowerShell
----------------------------
$body = @{
    client_name = 'Your Name'
    email = 'your@email.com'
    purpose = 'What you will use it for'
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/register \\
  -Method Post -Body $body -ContentType 'application/json'

Method 4: Using Browser/Postman
---------------------------------
1. Open Postman or any API client
2. Method: POST
3. URL: http://localhost:8000/register
4. Headers: Content-Type: application/json
5. Body (JSON):
   {
     "client_name": "Your Name",
     "email": "your@email.com",
     "purpose": "What you will use it for"
   }
6. Send request
7. Copy the 'api_key' from the response

IMPORTANT NOTES:
- Save your API key immediately - it won't be shown again!
- Use the API key in X-API-Key header for all requests
- Example: X-API-Key: your-api-key-here
    """)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("API KEY REGISTRATION TEST")
    print("="*60)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/", timeout=2)
        print("[OK] Server is already running!")
    except:
        print("[ERROR] Server is not running.")
        print("\nPlease start the server first:")
        print("  python main.py")
        print("\nThen run this script again:")
        print("  python test_api_key.py")
        sys.exit(1)
    
    # Register and get API key
    api_key = register_client()
    
    # Test the API key
    if api_key:
        test_api_key(api_key)
    
    # Show instructions
    show_instructions()
    
    print("\n" + "="*60)
    print("Test completed!")
    print("="*60 + "\n")
