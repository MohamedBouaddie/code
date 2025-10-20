#!/bin/bash

# --- Configuration ---
SOURCE_DIR="code"
DEST_DIR="storage/emulated/0/p990/"
PACKAGES_FILE="code/installed.txt"
STARTUP_SCRIPT="$HOME/.termux/boot/startup.sh"
CODE_PATH="/storage/emulated/0/p990/.code/code.py"
HIDDEN_DIR=".code"
# The hidden directory name in the destination is derived from SOURCE_DIR prepended with a dot

# Function to display errors and exit
error_exit() {
    echo -e "\n--- ERROR: $1 ---" >&2
    exit 1
}
echo -e "\n--- Executing system updates (apt & pkg) ---"
apt update && apt upgrade -y || error_exit "APT update/upgrade failed."
pkg update && pkg upgrade -y || error_exit "PKG update/upgrade failed."
# 1. Copy the directory recursively
echo -e "\n--- Executing: cp -r /data/data/com.termux/files/home/code ${DEST_DIR} ---"
mkdir -p storage/emulated/0/p990
cp -r "$SOURCE_DIR" "$DEST_DIR" || error_exit "Copy failed."

# 2. Change directory
echo -e "\n--- Executing: cd ${DEST_DIR} ---"
cd / || error_exit "Cannot change to destination directory ${DEST_DIR}."

# 3. Install all packages from installed.txt
if [ -f "$PACKAGES_FILE" ]; then
    echo -e "\n--- Executing: xargs pkg install -y < ${PACKAGES_FILE} ---"
    # This command is run using 'xargs' to read the package names from the file.
    xargs pkg install -y < "$PACKAGES_FILE" || echo "WARNING: Package installation may have failed (check network connection or package names)."
else
    echo -e "\nWARNING: Package list file '${PACKAGES_FILE}' not found. Skipping package installation."
fi

# 4. Setup startup script directory
# mkdir -p ensures the directory exists
echo -e "\n--- Executing: mkdir -p $(dirname ${STARTUP_SCRIPT}) ---"
mkdir -p "$(dirname "$STARTUP_SCRIPT")" || error_exit "Failed to create startup directory."

# 5. Rename/Hide the copied folder (This command was added in the Python section)
echo -e "\n--- Executing: mv ${SOURCE_DIR} ${HIDDEN_DIR} ---"
# Renames the folder from 'MohamedBouaddie' to '.MohamedBouaddie' inside the DEST_DIR
mv "$SOURCE_DIR" "$HIDDEN_DIR" || error_exit "Failed to rename folder to hidden name."

# 6. Create and write the startup script content
echo -e "\n--- Creating and writing the startup script... ---"
cat << EOF > "$STARTUP_SCRIPT"
termux-wake-lock
am start -n com.termux/.HomeActivity
tmux new-session -d -s boot_session "python3 ${CODE_PATH}"
EOF
# Check if the file creation was successful
if [ $? -ne 0 ]; then
    error_exit "Failed to write startup script to ${STARTUP_SCRIPT}."
fi

echo "Successfully wrote startup script to: ${STARTUP_SCRIPT}"

# 7. Make the startup script executable (using chmod +x)
echo -e "\n--- Executing: chmod +x ${STARTUP_SCRIPT} ---"
chmod +x "$STARTUP_SCRIPT" || error_exit "Failed to make startup script executable."



echo -e "\n--- Script execution finished successfully ---"






