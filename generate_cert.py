"""
Generate self-signed SSL certificate for HTTPS development
"""
import subprocess
import sys
from pathlib import Path

def generate_self_signed_cert():
    """Generate self-signed SSL certificate using OpenSSL"""
    
    # Create certs directory if it doesn't exist
    certs_dir = Path("certs")
    certs_dir.mkdir(exist_ok=True)
    
    cert_file = certs_dir / "server.crt"
    key_file = certs_dir / "server.key"
    
    # Check if OpenSSL is available
    try:
        subprocess.run(["openssl", "version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ OpenSSL not found!")
        print("\nPlease install OpenSSL:")
        print("  Windows: Download from https://slproweb.com/products/Win32OpenSSL.html")
        print("  Or use: choco install openssl")
        print("  Linux: sudo apt-get install openssl")
        print("  Mac: brew install openssl")
        return False
    
    # Generate certificate
    print("🔐 Generating self-signed SSL certificate...")
    
    try:
        # Generate private key
        subprocess.run([
            "openssl", "genrsa",
            "-out", str(key_file),
            "2048"
        ], check=True)
        print(f"✓ Generated private key: {key_file}")
        
        # Generate certificate
        subprocess.run([
            "openssl", "req",
            "-new", "-x509",
            "-key", str(key_file),
            "-out", str(cert_file),
            "-days", "365",
            "-subj", "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        ], check=True)
        print(f"✓ Generated certificate: {cert_file}")
        
        print("\n✅ SSL certificates generated successfully!")
        print(f"\n📁 Certificate files:")
        print(f"   Certificate: {cert_file.absolute()}")
        print(f"   Private Key: {key_file.absolute()}")
        print(f"\n⚠️  Note: This is a self-signed certificate for development only.")
        print(f"   Browsers will show a security warning - this is normal for self-signed certs.")
        print(f"   For production, use certificates from a trusted CA (Let's Encrypt, etc.)")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating certificate: {e}")
        return False

if __name__ == "__main__":
    success = generate_self_signed_cert()
    sys.exit(0 if success else 1)
