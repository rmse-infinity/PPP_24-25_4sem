
def main():
    import subprocess
    import time
    import os
    script_path = os.path.dirname(os.path.abspath(__file__))
    
    server_script = os.path.join(script_path, "server", "server.py")
    client_script = os.path.join(script_path, "klient", "klient.py")
    
    server_process = subprocess.Popen(["python3", server_script])
    
    time.sleep(1)
    
    client_process = subprocess.Popen(["python3", client_script])
    
    server_process.wait()
    client_process.wait()

    pass

if __name__ == "__main__":
    main()

