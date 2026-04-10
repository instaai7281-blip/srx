import subprocess
import time
import sys
import os

def run_bot():
    venv_python = sys.executable
    if not os.path.exists(venv_python):
        print(f"Error: {venv_python} not found.")
        return

    while True:
        print("Starting Bot...")
        try:
            # Start the bot as a subprocess
            process = subprocess.Popen([venv_python, "-m", "devgagan"])
            
            # Wait for the process to complete
            process.wait()
            
            # Exit code -1073741510 is Ctrl+C, but we should restart if it stops unexpectedly
            print(f"Bot stopped with exit code {process.returncode}. Restarting in 5 seconds...")
        except Exception as e:
            print(f"An error occurred: {e}. Restarting in 5 seconds...")
        
        time.sleep(5)

if __name__ == "__main__":
    run_bot()
