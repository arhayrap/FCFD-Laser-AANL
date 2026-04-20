import os
import shutil
import glob
import subprocess

LECROY_IP = "192.168.0.170"
BASE_PATH = "/home/arcadia/Documents"
MOUNT_POINT = "/mnt"
DEST_DIR = os.path.join(BASE_PATH, "Old_data_from_lecroy")  # Folder where files will be copied

# DEST_DIR = os.path.join(BASE_PATH, "test")


# Mount the oscilloscope's shared folder
mount_cmd = [
    "sudo", "mount", "-t", "cifs",
    f"//{LECROY_IP}/Waveforms",
    MOUNT_POINT,
    "-o", "username=lcrydmin"
]
umount_cmd = ["sudo", "umount", MOUNT_POINT]

print(f"Running: {' '.join(mount_cmd)}")
mount_proc = subprocess.run(mount_cmd, capture_output=True, text=True)

if mount_proc.returncode != 0:
    print("Mount failed:")
    print(mount_proc.stderr)
else:
    print("Mount successful.")

    # Match all .trc files from all channels
    pattern = os.path.join(MOUNT_POINT, "C1*140.trc")
    candidate_files = glob.glob(pattern)

    if not candidate_files:
        print("No .trc files found in the oscilloscope directory.")
    else:
        print(f"Found {len(candidate_files)} .trc files. Copying them...")

        os.makedirs(DEST_DIR, exist_ok=True)

        for filepath in candidate_files:
            try:
                shutil.copy(filepath, DEST_DIR)
                print(f"Copied {os.path.basename(filepath)}")
            except Exception as e:
                print(f"Failed to copy {filepath}: {e}")

    # Unmount after copying
    subprocess.run(umount_cmd)

