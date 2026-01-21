"""
Simple script to get your API key
Make sure the server is running first: python main.py
"""
import requests
import json

print("\n" + "="*60)
print("API KEY REGISTRATION")
print("="*60)

# Register to get API key
registration_data = {
    'client_name': input('Enter your name: '),
    'email': input('Enter your email: '),
    'purpose': input('What will you use this API for? ')
}

print("\nRegistering...")

try:
    response = requests.post(
        'http://localhost:8000/register',
        json=registration_data,
        timeout=5
    )
    
    if response.status_code == 200:
        result = response.json()
        print("\n" + "="*60)
        print("SUCCESS! YOUR API KEY:")
        print("="*60)
        print("\n" + result['api_key'])
        print("\n" + "="*60)
        print("\n[IMPORTANT] Save this key immediately!")
        print("It will NOT be shown again.\n")
        print(f"Message: {result['message']}\n")
    else:
        print(f"\n[ERROR] Registration failed: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("\n[ERROR] Cannot connect to server!")
    print("Make sure the server is running:")
    print("  python main.py")
except Exception as e:
    print(f"\n[ERROR] {e}")
