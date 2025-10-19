
import os
import subprocess
import sys

# --- Configuration ---
SOURCE_DIR = "MohamedBouaddie"
DEST_DIR = "storage/emulated/0/p990/"
PACKAGES_FILE = "installed.txt"
STARTUP_SCRIPT_PATH = os.path.expanduser("~/.termux/boot/startup.sh")

# --- Helper function to run shell commands ---
def run_command(command, check=True):
    """Executes a shell command and prints the output."""
    print(f"\n--- Executing: {command} ---")
    try:
        # Using subprocess.run for better control and error handling
        result = subprocess.run(
            command,
            shell=True,
            check=check, # Raises CalledProcessError if the command returns a non-zero exit code
            text=True,
            capture_output=True
        )
        print("STDOUT:\n", result.stdout)
        if result.stderr:
            print("STDERR:\n", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"\n--- ERROR executing command: {command} ---")
        print(f"Return code: {e.returncode}")
        print("Output:", e.output)
        print("Stderr:", e.stderr)
        # Exit the script upon critical failure
        sys.exit(1)
    except FileNotFoundError:
        print(f"ERROR: Command or executable not found for: {command}")
        sys.exit(1)


# 1. Copy the directory recursively
print("1. Copying directory...")
run_command(f"cp -r {SOURCE_DIR} {DEST_DIR}")

# 2. Change directory
print("2. Changing directory (using os.chdir for Python's current working directory)...")
try:
    os.chdir(DEST_DIR)
    print(f"Current working directory is now: {os.getcwd()}")
except FileNotFoundError:
    print(f"Error: Destination directory {DEST_DIR} not found. Exiting.")
    sys.exit(1)


# 3. Install all packages from installed.txt
print("3. Installing packages...")
# Note: This assumes 'installed.txt' is in the current working directory or accessible.
if os.path.exists(PACKAGES_FILE):
    run_command(f"xargs pkg install -y < {PACKAGES_FILE}")
else:
    print(f"WARNING: Package list file '{PACKAGES_FILE}' not found. Skipping package installation.")


# 4. Setup startup script directory
# The 'mkdir -p' command ensures the directory exists
print("4. Creating Termux boot directory...")
run_command(f"mkdir -p {os.path.dirname(STARTUP_SCRIPT_PATH)}")


# 5. Create and write the startup script content
print("5. Creating and writing the startup script...")
startup_script_content = """termux-wake-lock
am start -n com.termux/.HomeActivity
tmux new-session -d -s boot_session 'python3 /storage/emulated/0/p990/.MohamedBouaddie/code.py'
"""
# Note: The original script had a typo on the last line (.termux/boot/startup.sh),
# and the chmod command was also referencing a wrong file (start.sh instead of startup.sh).
# The path for 'code.py' in the startup script is derived from the initial copy operation.

try:
    with open(STARTUP_SCRIPT_PATH, "w") as f:
        f.write(startup_script_content.strip())
    print(f"Successfully wrote startup script to: {STARTUP_SCRIPT_PATH}")
except IOError as e:
    print(f"Error writing startup script: {e}")
    sys.exit(1)


# 6. Make the startup script executable (using chmod +x)
print("6. Making the startup script executable...")
# Correcting the final command from the original shell script to use 'startup.sh'
run_command(f"chmod +x {STARTUP_SCRIPT_PATH}")


print("\n--- Script execution finished ---")