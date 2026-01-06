#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# --- Configuration ---
SOURCE_DIR = "/home/brothergelbert/Pictures"
BACKUP_DIR = "/home/brothergelbert/fleem" ##Should also be the mount point for the MOUNT_DEVICE
MOUNT_DEVICE = "//192.168.1.90/shmee"
SIZE_THRESHOLD_MB = 100  # Threshold in Gigabytes
# ---------------------

def mount_directory(mount_point, device):
    try:
    # Create the mount point if it doesn't exist
        if not os.path.exists(mount_point):
            os.makedirs(mount_point)
            print(f"Created mount point: {mount_point}")

    # Check if the device is already mounted
        if not os.path.ismount(mount_point):
        # Execute the mount command
        # The list format is safer as it avoids shell injection vulnerabilities
            subprocess.check_call(["mount", "-t cifs", "-o username=Brothergelbert,password=Loverainbow1!", device, mount_point])
            print(f"Successfully mounted {device} to {mount_point}")
        else:
            print(f"{device} is already mounted at {mount_point}")

    except subprocess.CalledProcessError as e:
        print(f"Error mounting: {e}")
        print(f"Stderr: {e.stderr.decode('utf-8') if e.stderr else 'N/A'}")
    except FileNotFoundError:
        print("Error: 'mount' command not found. Ensure it's in your system's PATH.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")	

def get_dir_size(path):
    """Calculates the total size of a directory in bytes."""
    total_size = 0
    try:
        for entry in Path(path).rglob('*'):
            if entry.is_file():
                total_size += entry.stat().st_size
    except FileNotFoundError:
        print(f"Error: Source directory not found at {path}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while calculating directory size: {e}")
        sys.exit(1)
    return total_size

def run_backup(source, destination):
    """Executes the rsync command for backup."""
    # Create a timestamped directory for the current backup
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    destination_path = Path(destination) / f"backup_{timestamp}"
    destination_path.mkdir(parents=True, exist_ok=True)

    print(f"Directory size exceeds threshold. Starting backup to {destination_path}...")
    
    # Use rsync for an efficient backup. Options include:
    # -a: archive mode (preserves permissions, timestamps, etc.)
    # -v: verbose
    # --delete: deletes files in the destination that are not in the source
    # Note: For Time Machine style incremental backups with hardlinking unchanged files, 
    # you might need a more sophisticated script or dedicated tool like rsnapshot or rsync-time-machine.py.
    rsync_cmd = ["rsync", "-av", "--delete", str(source), str(destination_path)]
    
    try:
        subprocess.run(rsync_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Backup completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Backup failed. Stderr: {e.stderr.decode()}")
        print(f"Stdout: {e.stdout.decode()}")
        sys.exit(1)

def main():
    # Convert threshold to bytes
    threshold_bytes = SIZE_THRESHOLD_MB * 1024 * 1024

    current_size = get_dir_size(SOURCE_DIR)
    print(f"Current directory size: {current_size / (1024*1024):.2f} MB")

    if current_size >= threshold_bytes:
        mount_directory(BACKUP_DIR, MOUNT_DEVICE)
        run_backup(SOURCE_DIR, BACKUP_DIR)
    else:
        print("Directory size is within the limit. No backup needed at this time.")

if __name__ == "__main__":
    main()
