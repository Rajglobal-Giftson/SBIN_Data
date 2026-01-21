"""
Check if port 8000 is in use and help resolve the issue
"""
import socket
import subprocess
import sys

def check_port(port):
    """Check if a port is in use"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def find_process_using_port(port):
    """Find process using the port (Windows)"""
    try:
        # Use netstat to find the process
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True,
            text=True
        )
        
        for line in result.stdout.split('\n'):
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    return pid
        return None
    except:
        return None

def main():
    port = 8000
    print(f"\n{'='*60}")
    print("PORT 8000 STATUS CHECK")
    print("="*60)
    
    if check_port(port):
        print(f"\n[WARNING] Port {port} is already in use!")
        print("\nThis means the server is already running.")
        print("\nOptions:")
        print("  1. Use the existing server (it's already running)")
        print("  2. Stop the existing server and start a new one")
        print("  3. Use a different port")
        
        pid = find_process_using_port(port)
        if pid:
            print(f"\nProcess using port {port}: PID {pid}")
            print("\nTo stop it:")
            print(f"  taskkill /PID {pid} /F")
            print("\nOr find it in Task Manager and end the process.")
        else:
            print("\nCould not find the process ID automatically.")
            print("Check Task Manager for Python processes.")
        
        print("\n" + "="*60)
        return False
    else:
        print(f"\n[OK] Port {port} is available!")
        print("You can start the server now.")
        print("\n" + "="*60)
        return True

if __name__ == "__main__":
    main()
