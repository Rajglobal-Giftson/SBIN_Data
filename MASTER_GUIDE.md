# Stock Market TBT Backend - Master Guide

This single guide replaces the following files:
- `HOW_TO_RUN.md`
- `HOW_IT_WORKS.md`
- `GET_API_KEY_GUIDE.md`
- `FIX_PORT_ERROR.md`
- `CONNECTION_GUIDE.md`
- `CLIENT_GUIDE.md`
- `BROWSER_ACCESS_FIX.md`

---

## Table of Contents

1. Quick Start
2. Configuration
3. HTTPS vs HTTP
4. Verify the Server
5. Get an API Key
6. Use the API (Examples)
7. Connection Guide (Local/Network/Public)
8. Troubleshooting
9. How the System Works (Architecture)

---

## 1) Quick Start

### Prerequisites
- Python 3.9–3.12 installed (pandas 2.1.3 does not support 3.13/3.14)
- Data directory exists at: `E:\Project\Version\RajBE\Data\Zoho WorkDrive\`

### Install Dependencies
```bash
cd E:\Project\Version\RajBE\Data
pip install -r requirements.txt
```

### (Optional) Generate HTTPS Certificates
```bash
python generate_cert.py
```

### Start the Server
```bash
python main.py
```

**Expected output (HTTP):**
```
[STARTING] Starting HTTP server on http://0.0.0.0:8000
[INFO] Access the server at:
       http://localhost:8000
       http://127.0.0.1:8000
[NOTE] Do NOT use http://0.0.0.0:8000 in browser!
```

**Expected output (HTTPS):**
```
[OK] HTTPS enabled with certificates
[STARTING] Starting HTTPS server on https://0.0.0.0:8000
[INFO] Access the server at:
       https://localhost:8000
       https://127.0.0.1:8000
```

---

## 2) Configuration

Create a `.env` file in the project root:

```env
# API Keys (comma-separated list)
API_KEYS=key1,key2,key3

# Admin Key for administrative operations
ADMIN_KEY=admin-secret-key-change-this

# HTTPS Configuration
USE_HTTPS=true
SSL_CERT_FILE=certs/server.crt
SSL_KEY_FILE=certs/server.key
```

**Defaults if `.env` is missing:**
- API_KEYS: `default-api-key-12345-change-this`
- ADMIN_KEY: `admin-secret-key-change-this`
- USE_HTTPS: `true` (falls back to HTTP if certs missing)
- SSL_CERT_FILE: `certs/server.crt`
- SSL_KEY_FILE: `certs/server.key`

---

## 3) HTTPS vs HTTP

### HTTPS (Default, Recommended)
- Encrypted connections
- Required for production
- Self-signed certs show browser warnings (dev only)
- Use `-k` in curl, `verify=False` in Python for self-signed certs

### HTTP (Development Only)
- No encryption
- Set `USE_HTTPS=false` in `.env`
- Never use HTTP in production

---

## 4) Verify the Server

### Browser
- HTTP: `http://localhost:8000`
- HTTPS: `https://localhost:8000` (accept warning if self-signed)

### Swagger / ReDoc
- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

### Test Script
```bash
python test_server.py
```

---

## 5) Get an API Key

### Option A: Python Script
Create `get_my_api_key.py`:
```python
import requests

BASE_URL = "http://localhost:8000"  # use https:// if HTTPS enabled
VERIFY_SSL = False  # True for production certs

response = requests.post(
    f"{BASE_URL}/register",
    json={
        "client_name": "Your Name Here",
        "email": "your-email@example.com",
        "purpose": "Stock market data analysis"
    },
    verify=VERIFY_SSL
)
response.raise_for_status()
api_key = response.json()["api_key"]
print("YOUR API KEY:", api_key)

with open("my_api_key.txt", "w") as f:
    f.write(api_key)
print("API key saved to my_api_key.txt")
```

Run it:
```bash
python get_my_api_key.py
```

### Option B: PowerShell
```powershell
$baseUrl = "http://localhost:8000"  # use https:// if HTTPS enabled
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}

$body = @{
    client_name = 'Your Name Here'
    email = 'your-email@example.com'
    purpose = 'Stock market data analysis'
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "$baseUrl/register" -Method Post -Body $body -ContentType 'application/json'
$response.api_key | Out-File -FilePath "my_api_key.txt" -Encoding utf8
Write-Host "API key saved to my_api_key.txt"
```

### Option C: cURL
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "Your Name Here",
    "email": "your-email@example.com",
    "purpose": "Stock market data analysis"
  }'
```

---

## 6) Use the API (Examples)

**Header:**
```
X-API-Key: your-api-key-here
```

### Get Tickers
```bash
curl -H "X-API-Key: YOUR_API_KEY_HERE" http://localhost:8000/tickers
```

### Get Data
```bash
curl -H "X-API-Key: YOUR_API_KEY_HERE" \
  "http://localhost:8000/data/SBIN?year=2025&month=1&limit=100"
```

### Python Example
```python
import requests

API_KEY = "your-api-key-here"
BASE_URL = "http://localhost:8000"

headers = {"X-API-Key": API_KEY}
response = requests.get(f"{BASE_URL}/tickers", headers=headers)
print(response.json())
```

---

## 7) Connection Guide (Local/Network/Public)

### Local
- `http://localhost:8000`
- `http://127.0.0.1:8000`

### Same Network
1. Find your server IP: `ipconfig`
2. Access:
   - `http://YOUR_IP:8000`

### Public Access (EC2 / Cloud)
- Open inbound port 8000 in security group/firewall
- Access:
  - `http://EC2_PUBLIC_IP:8000`

---

## 8) Troubleshooting

### Browser shows ERR_ADDRESS_INVALID
Do **not** use `0.0.0.0` in a browser.
Use `http://localhost:8000` instead.

### Port 8000 already in use
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```
Or:
```bash
python stop_server.py
```

### Cannot connect
- Ensure server is running
- Try `http://127.0.0.1:8000`
- Check firewall rules

### SSL warnings
- Self-signed certs show warnings (expected in dev)
- Use valid certs in production

---

## 9) How the System Works (Architecture)

### Server
- FastAPI + Uvicorn
- Port 8000
- HTTP or HTTPS
- Binds to `0.0.0.0`

### Data
- CSV files under: `E:\Project\Version\RajBE\Data\Zoho WorkDrive\`
- Organized by year/month

### API Flow
1. Client registers at `/register`
2. Server generates API key and stores it
3. Client uses `X-API-Key` on protected endpoints
4. Server validates key and returns data

### Key Endpoints
- Public: `/`, `/register`
- Protected: `/health`, `/tickers`, `/data/{ticker}`, `/summary`, `/range`, `/dates`, `/latest`, `/stats`
- Admin: `/admin/generate-key`, `/admin/keys`

---

**Master guide complete.**
