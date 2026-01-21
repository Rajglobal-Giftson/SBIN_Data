"""
Stop the server running on port 8000
"""
import subprocess
import socket

def find_process_on_port(port):
    """Find process ID using the port"""
    try:
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

def stop_process(pid):
    """Stop a process by PID"""
    try:
        subprocess.run(['taskkill', '/PID', str(pid), '/F'], 
                      capture_output=True, check=True)
        return True
    except:
        return False

def main():
    port = 8000
    print(f"\n{'='*60}")
    print("STOP SERVER ON PORT 8000")
    print("="*60)
    
    # Check if port is in use
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    
    if result == 0:
        print(f"\n[INFO] Port {port} is in use.")
        pid = find_process_on_port(port)
        
        if pid:
            print(f"[INFO] Found process: PID {pid}")
            print("[INFO] Stopping server...")
            
            if stop_process(pid):
                print(f"[OK] Server stopped successfully!")
                print(f"     Process {pid} terminated.")
            else:
                print(f"[ERROR] Could not stop process {pid}")
                print("     Try running as administrator or use Task Manager")
        else:
            print("[ERROR] Could not find process ID")
            print("     Use Task Manager to find and stop Python processes")
    else:
        print(f"\n[INFO] Port {port} is not in use.")
        print("     No server to stop.")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
