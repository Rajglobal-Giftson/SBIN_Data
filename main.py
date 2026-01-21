from fastapi import FastAPI, HTTPException, Query, Depends, Security, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from typing import Optional, List
from pydantic import BaseModel
import pandas as pd
from pathlib import Path
import os
import secrets
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Stock Market TBT Backend", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data directory path
DATA_DIR = Path(r"E:\Project\Version\RajBE\Data\Zoho WorkDrive")

# SSL/TLS Configuration
SSL_CERT_FILE = os.getenv("SSL_CERT_FILE", "certs/server.crt")
SSL_KEY_FILE = os.getenv("SSL_KEY_FILE", "certs/server.key")
USE_HTTPS = os.getenv("USE_HTTPS", "true").lower() == "true"

# API Key Configuration
API_KEY_NAME = "X-API-Key"
API_KEYS = os.getenv("API_KEYS", "default-api-key-12345-change-this").split(",")
API_KEYS_FILE = Path("api_keys.json")  # File to store generated API keys

# Admin Key for managing API keys (set in .env)
ADMIN_KEY = os.getenv("ADMIN_KEY", "admin-secret-key-change-this")

# API Key Security
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
admin_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)

def load_api_keys_from_file():
    """Load API keys from JSON file"""
    if API_KEYS_FILE.exists():
        try:
            with open(API_KEYS_FILE, 'r') as f:
                data = json.load(f)
                return data.get('keys', [])
        except:
            return []
    return []

def save_api_keys_to_file(keys: List[str]):
    """Save API keys to JSON file"""
    data = {
        'keys': keys,
        'last_updated': datetime.now().isoformat()
    }
    with open(API_KEYS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_all_valid_keys():
    """Get all valid API keys (from env + file)"""
    env_keys = [key.strip() for key in API_KEYS if key.strip()]
    file_keys = load_api_keys_from_file()
    return list(set(env_keys + file_keys))

async def verify_admin_key(admin_key: Optional[str] = Security(admin_key_header)):
    """Verify admin key for administrative operations"""
    if not admin_key:
        raise HTTPException(
            status_code=401,
            detail="Admin key missing. Please provide X-Admin-Key header."
        )
    if admin_key.strip() != ADMIN_KEY.strip():
        raise HTTPException(
            status_code=403,
            detail="Invalid admin key. Access denied."
        )
    return admin_key

async def verify_api_key(api_key: Optional[str] = Security(api_key_header)):
    """Verify API key from request header"""
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key missing. Please provide X-API-Key header."
        )
    
    # Check if API key is valid (trimmed for comparison)
    api_key_clean = api_key.strip()
    valid_keys = get_all_valid_keys()
    
    if api_key_clean not in [key.strip() for key in valid_keys]:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key. Access denied."
        )
    
    return api_key_clean

class StockTick(BaseModel):
    Ticker: str
    Date: int
    Time: str
    Close: float
    Volume: int
    OI: int
    Bid: float
    BidQty: int
    Ask: float
    AskQty: int

class StockTicksResponse(BaseModel):
    data: List[dict]
    total: int
    ticker: str
    date_range: str

def get_csv_path(year: int, month: int, ticker: str) -> Optional[Path]:
    """Get the path to CSV file for given year, month, and ticker"""
    month_str = f"{month:02d}-{year}"
    file_path = DATA_DIR / str(year) / month_str / f"{ticker}.csv"
    if file_path.exists():
        return file_path
    return None

def load_ticker_data(ticker: str, year: Optional[int] = None, month: Optional[int] = None) -> pd.DataFrame:
    """Load ticker data from CSV files"""
    all_data = []
    
    if year and month:
        # Load specific month
        file_path = get_csv_path(year, month, ticker)
        if file_path:
            df = pd.read_csv(file_path)
            all_data.append(df)
    else:
        # Load all available data for the ticker
        # Check both 2024 and 2025 directories
        for year_dir in [2024, 2025]:
            year_path = DATA_DIR / str(year_dir)
            if year_path.exists():
                for month_dir in year_path.iterdir():
                    if month_dir.is_dir():
                        file_path = month_dir / f"{ticker}.csv"
                        if file_path.exists():
                            df = pd.read_csv(file_path)
                            all_data.append(df)
    
    if not all_data:
        return pd.DataFrame()
    
    # Combine all dataframes
    combined_df = pd.concat(all_data, ignore_index=True)
    return combined_df

class APIKeyRequest(BaseModel):
    client_name: str
    email: Optional[str] = None
    purpose: Optional[str] = None

class APIKeyResponse(BaseModel):
    api_key: str
    message: str
    expires: Optional[str] = None

@app.get("/")
async def root():
    """Root endpoint - No API key required"""
    protocol = "https" if USE_HTTPS else "http"
    return {
        "message": "Stock Market TBT Backend API",
        "version": "1.0.0",
        "protocol": protocol.upper(),
        "authentication": "All endpoints (except public ones) require API key in X-API-Key header",
        "public_endpoints": {
            "root": "/",
            "register": "/register - Request API key"
        },
        "api_endpoints": {
            "health": "/health",
            "tickers": "/tickers",
            "data": "/data/{ticker}",
            "date_range": "/data/{ticker}/range",
            "summary": "/data/{ticker}/summary",
            "dates": "/data/{ticker}/dates",
            "latest": "/data/{ticker}/latest",
            "stats": "/data/{ticker}/stats"
        },
        "admin_endpoints": {
            "generate_key": "/admin/generate-key - Generate new API key (requires admin key)",
            "list_keys": "/admin/keys - List all API keys (requires admin key)"
        },
        "how_to_get_api_key": {
            "method": "POST",
            "url": f"{protocol}://your-server:8000/register",
            "body": {
                "client_name": "Your Name or Company",
                "email": "your-email@example.com",
                "purpose": "Brief description of usage"
            }
        },
        "example_request": {
            "method": "GET",
            "url": f"{protocol}://your-server:8000/tickers",
            "headers": {
                "X-API-Key": "your-api-key-here"
            }
        }
    }

@app.post("/register", response_model=APIKeyResponse)
async def register_client(request: APIKeyRequest):
    """
    Register as a client and get an API key
    No authentication required - public endpoint
    """
    # Generate a new API key
    new_api_key = secrets.token_urlsafe(32)
    
    # Load existing keys
    existing_keys = load_api_keys_from_file()
    
    # Add new key
    existing_keys.append(new_api_key)
    
    # Save to file
    save_api_keys_to_file(existing_keys)
    
    # Log registration (optional - you can save to a file or database)
    registration_log = {
        "client_name": request.client_name,
        "email": request.email,
        "purpose": request.purpose,
        "api_key": new_api_key,
        "registered_at": datetime.now().isoformat()
    }
    
    # Save registration info (optional)
    log_file = Path("registrations.json")
    registrations = []
    if log_file.exists():
        try:
            with open(log_file, 'r') as f:
                registrations = json.load(f)
        except:
            pass
    
    registrations.append(registration_log)
    with open(log_file, 'w') as f:
        json.dump(registrations, f, indent=2)
    
    return APIKeyResponse(
        api_key=new_api_key,
        message=f"API key generated successfully for {request.client_name}. Please save this key securely - it will not be shown again!",
        expires=None
    )

@app.post("/admin/generate-key", response_model=APIKeyResponse)
async def generate_api_key(
    client_name: str = Query(..., description="Name of the client"),
    admin_key: str = Depends(verify_admin_key)
):
    """
    Generate a new API key (Admin only)
    Requires X-Admin-Key header
    """
    # Generate a new API key
    new_api_key = secrets.token_urlsafe(32)
    
    # Load existing keys
    existing_keys = load_api_keys_from_file()
    
    # Add new key
    existing_keys.append(new_api_key)
    
    # Save to file
    save_api_keys_to_file(existing_keys)
    
    return APIKeyResponse(
        api_key=new_api_key,
        message=f"API key generated for {client_name}",
        expires=None
    )

@app.get("/admin/keys")
async def list_api_keys(admin_key: str = Depends(verify_admin_key)):
    """
    List all API keys (Admin only)
    Requires X-Admin-Key header
    """
    env_keys = [key.strip() for key in API_KEYS if key.strip()]
    file_keys = load_api_keys_from_file()
    
    return {
        "total_keys": len(env_keys) + len(file_keys),
        "env_keys_count": len(env_keys),
        "file_keys_count": len(file_keys),
        "env_keys": env_keys,  # Show first 3 chars for security
        "file_keys": [key[:8] + "..." for key in file_keys] if file_keys else [],
        "note": "Full keys are only shown in env_keys (from .env file). File keys are truncated for security."
    }

@app.get("/health")
async def health_check(api_key: str = Depends(verify_api_key)):
    """Health check endpoint - Requires API key"""
    return {
        "status": "healthy",
        "data_directory": str(DATA_DIR),
        "api_key_valid": True
    }

@app.get("/tickers")
async def get_available_tickers(api_key: str = Depends(verify_api_key)):
    """Get list of available tickers - Requires API key"""
    tickers = set()
    
    for year_dir in [2024, 2025]:
        year_path = DATA_DIR / str(year_dir)
        if year_path.exists():
            for month_dir in year_path.iterdir():
                if month_dir.is_dir():
                    for file in month_dir.glob("*.csv"):
                        ticker = file.stem  # Get filename without extension
                        tickers.add(ticker)
    
    return {
        "tickers": sorted(list(tickers)),
        "count": len(tickers)
    }

@app.get("/data/{ticker}", response_model=StockTicksResponse)
async def get_ticker_data(
    ticker: str,
    api_key: str = Depends(verify_api_key),
    year: Optional[int] = Query(None, description="Filter by year (e.g., 2025)"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month (1-12)"),
    date: Optional[int] = Query(None, description="Filter by specific date (YYYYMMDD format)"),
    limit: Optional[int] = Query(1000, ge=1, le=10000, description="Maximum number of records to return"),
    offset: Optional[int] = Query(0, ge=0, description="Offset for pagination")
):
    """Get tick-by-tick data for a specific ticker - Requires API key"""
    try:
        # Load data
        df = load_ticker_data(ticker, year, month)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker}")
        
        # Filter by date if provided
        if date:
            df = df[df['Date'] == date]
        
        # Sort by Date and Time
        df = df.sort_values(['Date', 'Time'])
        
        # Apply pagination
        total = len(df)
        df = df.iloc[offset:offset+limit]
        
        # Convert to list of dictionaries
        data = df.to_dict('records')
        
        # Get date range
        if len(df) > 0:
            min_date = int(df['Date'].min())
            max_date = int(df['Date'].max())
            date_range = f"{min_date} to {max_date}"
        else:
            date_range = "N/A"
        
        return StockTicksResponse(
            data=data,
            total=total,
            ticker=ticker,
            date_range=date_range
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")

@app.get("/data/{ticker}/range")
async def get_ticker_date_range(
    ticker: str,
    api_key: str = Depends(verify_api_key),
    start_date: int = Query(..., description="Start date (YYYYMMDD format)"),
    end_date: int = Query(..., description="End date (YYYYMMDD format)"),
    limit: Optional[int] = Query(1000, ge=1, le=10000, description="Maximum number of records to return"),
    offset: Optional[int] = Query(0, ge=0, description="Offset for pagination")
):
    """Get tick-by-tick data for a specific ticker within a date range - Requires API key"""
    try:
        # Load all data for ticker
        df = load_ticker_data(ticker)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker}")
        
        # Filter by date range
        df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker} in the specified date range")
        
        # Sort by Date and Time
        df = df.sort_values(['Date', 'Time'])
        
        # Apply pagination
        total = len(df)
        df = df.iloc[offset:offset+limit]
        
        # Convert to list of dictionaries
        data = df.to_dict('records')
        
        return StockTicksResponse(
            data=data,
            total=total,
            ticker=ticker,
            date_range=f"{start_date} to {end_date}"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")

@app.get("/data/{ticker}/summary")
async def get_ticker_summary(ticker: str, api_key: str = Depends(verify_api_key)):
    """Get summary statistics for a ticker - Requires API key"""
    try:
        df = load_ticker_data(ticker)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker}")
        
        return {
            "ticker": ticker,
            "total_records": len(df),
            "date_range": {
                "start": int(df['Date'].min()),
                "end": int(df['Date'].max())
            },
            "price_range": {
                "min": float(df['Close'].min()),
                "max": float(df['Close'].max()),
                "avg": float(df['Close'].mean())
            },
            "total_volume": int(df['Volume'].sum()),
            "unique_dates": int(df['Date'].nunique())
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")

@app.get("/data/{ticker}/dates")
async def get_ticker_dates(ticker: str, api_key: str = Depends(verify_api_key)):
    """Get list of available dates for a ticker - Requires API key"""
    try:
        df = load_ticker_data(ticker)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker}")
        
        dates = sorted(df['Date'].unique().tolist())
        
        return {
            "ticker": ticker,
            "dates": dates,
            "count": len(dates),
            "date_range": {
                "start": int(min(dates)),
                "end": int(max(dates))
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")

@app.get("/data/{ticker}/latest")
async def get_ticker_latest(ticker: str, api_key: str = Depends(verify_api_key)):
    """Get the latest tick data for a ticker - Requires API key"""
    try:
        df = load_ticker_data(ticker)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker}")
        
        # Sort by Date and Time, get latest
        df_sorted = df.sort_values(['Date', 'Time'], ascending=[False, False])
        latest = df_sorted.iloc[0].to_dict()
        
        return {
            "ticker": ticker,
            "latest_tick": latest
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")

@app.get("/data/{ticker}/stats")
async def get_ticker_stats(
    ticker: str,
    api_key: str = Depends(verify_api_key),
    date: Optional[int] = Query(None, description="Filter by specific date (YYYYMMDD format)")
):
    """Get statistical analysis for a ticker (for a specific date or all time) - Requires API key"""
    try:
        df = load_ticker_data(ticker)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker}")
        
        # Filter by date if provided
        if date:
            df = df[df['Date'] == date]
            if df.empty:
                raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker} on date {date}")
        
        return {
            "ticker": ticker,
            "date": date if date else "all",
            "statistics": {
                "price": {
                    "open": float(df.iloc[0]['Close']),
                    "close": float(df.iloc[-1]['Close']),
                    "high": float(df['Close'].max()),
                    "low": float(df['Close'].min()),
                    "mean": float(df['Close'].mean()),
                    "std": float(df['Close'].std()),
                    "median": float(df['Close'].median())
                },
                "volume": {
                    "total": int(df['Volume'].sum()),
                    "mean": float(df['Volume'].mean()),
                    "max": int(df['Volume'].max()),
                    "min": int(df['Volume'].min())
                },
                "bid_ask": {
                    "avg_bid": float(df['Bid'].mean()),
                    "avg_ask": float(df['Ask'].mean()),
                    "avg_spread": float((df['Ask'] - df['Bid']).mean())
                },
                "tick_count": len(df)
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # SSL Configuration
    ssl_keyfile = None
    ssl_certfile = None
    
    if USE_HTTPS:
        cert_path = Path(SSL_CERT_FILE)
        key_path = Path(SSL_KEY_FILE)
        
        if cert_path.exists() and key_path.exists():
            ssl_certfile = str(cert_path)
            ssl_keyfile = str(key_path)
            print(f"[OK] HTTPS enabled with certificates")
            print(f"  Certificate: {ssl_certfile}")
            print(f"  Key: {ssl_keyfile}")
        else:
            print(f"[WARNING] HTTPS requested but certificates not found!")
            print(f"  Looking for: {cert_path} and {key_path}")
            print(f"  Run 'python generate_cert.py' to create self-signed certificates")
            print(f"  Or set USE_HTTPS=false in .env to use HTTP")
            print(f"  Falling back to HTTP mode...")
            USE_HTTPS = False
    
    if USE_HTTPS and ssl_certfile and ssl_keyfile:
        print(f"\n[STARTING] Starting HTTPS server on https://0.0.0.0:8000")
        print(f"[INFO] Access the server at:")
        print(f"       https://localhost:8000")
        print(f"       https://127.0.0.1:8000")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile
        )
    else:
        print(f"\n[STARTING] Starting HTTP server on http://0.0.0.0:8000")
        print(f"[NOTE] For production, use HTTPS with valid SSL certificates")
        print(f"\n[INFO] Access the server at:")
        print(f"       http://localhost:8000")
        print(f"       http://127.0.0.1:8000")
        print(f"\n[NOTE] Do NOT use http://0.0.0.0:8000 in browser!")
        print(f"       0.0.0.0 is for server binding only, not for client access.\n")
        uvicorn.run(app, host="0.0.0.0", port=8000)
