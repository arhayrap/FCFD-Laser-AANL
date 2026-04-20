import libximc.highlevel as ximc
import pexpect
import time
import os
import subprocess
from logger import logger


# BASE_PATH = "/home/arcadia/Documents/Motors_automation_test/DAQtest"            # base path where the data will be copied
MOUNT_POINT = "/mnt/waveforms"
# umount_cmd = ["sudo", "umount", MOUNT_POINT]
# subprocess.run(umount_cmd)
# os.makedirs(MOUNT_POINT, exist_ok=True)
sh_script_path = "/home/arcadia/Documents/Motors_automation_test/TimingDAQ/script_FCFD.sh"

umount_cmd = ["sudo", "umount", MOUNT_POINT]


def GetLatestNumber():
    run_num_file = "/home/arcadia/Documents/Motors_automation_test/DAQtest/next_run_number.txt"
    FileHandle = open(run_num_file)
    latestNumber = int(FileHandle.read().strip())
    FileHandle.close()
    return latestNumber

def run_script_with_conditional_password(script_name):

    with open('/home/arcadia/Documents/Motors_automation_test/PASSWORDS.txt', 'r') as file:
        passwords = file.read().splitlines()  # Removes any accidental newline characters just in case
        # you will need to write your PC's password into 

    PC_PASSWORD = str(passwords[0])
    SCOPE_PASSWORD = str(passwords[1])


    child = pexpect.spawn(f"python {script_name}", encoding='utf-8')

    patterns = [
        r'\[sudo\] password for arcadia: ',  # The line in the terminal expected for entering the password for arcadia 
        r'Password for lcrydmin@//192.168.0.170/Waveforms: ', # same thing for the scope's password
        pexpect.EOF
    ]
    
    child.logfile = open("pexpect_log.txt", "w")

    while True:
        try:
            index = child.expect(patterns, timeout=60)
            if index == 0:
                print("Password prompt detected for arcadia!")
                child.sendline(PC_PASSWORD)

            elif index == 1:
                print("Password prompt detected for scope!")
                child.sendline(SCOPE_PASSWORD)

            elif index == 2:  # EOF (end of script)
                print(f"Finished running {script_name}")
                break
        except pexpect.exceptions.TIMEOUT:
            print("Timeout exceeded while waiting for prompt.")
            break
    child.wait()
    child.close()



# Motor setup and control
from motortools import Motor
# Main code execution
m = Motor()
m.initialize_devices()

# axis_input = 'X' # change if you want to scan alongside other axis
# axis_input = axis_input.upper()

position_calb_x, position_calb_y, position_calb_z = m.get_calb()
print("Initial position X:", position_calb_x.Position, "um")
print("Initial position Y:", position_calb_y.Position, "um")
print("Initial position Z:", position_calb_z.Position, "um\n")

nX = int(input("Please enter the number of steps in X direction: "))
move_X = float(input(f"Enter step length (X) in microns: "))

nZ = int(input("Please enter the number of steps in Z direction: "))
move_Z = float(input(f"Enter step length (Z) in microns: "))

# wait_time = int(input("Please enter the WAIT_TIME in miliseconds: "))
wait_time = 0


steps_remaining = nX * nZ

for iz in range(nZ):
    for ix in range(nX):
        position_calb_x, position_calb_y, position_calb_z = m.get_calb()
        print(f"\n\nSteps remaining: {steps_remaining}.")
        print(f"Doing run number {GetLatestNumber()}. Coordinates for this run are below:")
        print("Current position X:", position_calb_x.Position, "um")
        print("Current position Y:", position_calb_y.Position, "um")
        print("Current position Z:", position_calb_z.Position, "um\n")
        m.axis_x.command_wait_for_stop(1000)
        latest_run_number = str(GetLatestNumber())
        logger.info(f"Run number: {latest_run_number}, coordinates below")
        m.log_state()

        # # running the scripts and sending the password lines if the terminal requires them
        try: run_script_with_conditional_password("acquisition.py")
        except:
            print(f"Error occurred while running the script: {e}")
            logger.info(f"Error occurred while running the script: {e}")

        try: run_script_with_conditional_password("conversion.py")
        except: 
            print(f"Error occurred while running the script: {e}")
            logger.info(f"Error occurred while running the script: {e}")

        try:
            subprocess.run(['bash', sh_script_path, latest_run_number], check=True)
            print("Script executed successfully")
            logger.info("Script executed successfully")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while running the script: {e}")
            logger.info(f"Error occurred while running the script: {e}")

        m.move_XYZ_R(dX=move_X)        
        steps_remaining -= 1

    m.move_XYZ_R(dZ=move_Z)
    m.move_XYZ_R(dX=-nX*move_X)

    position_calb_x, position_calb_y, position_calb_z = m.get_calb()
    print("Final position X:", position_calb_x.Position, "um")
    print("Final position Y:", position_calb_y.Position, "um")
    print("Final position Z:", position_calb_z.Position, "um")


m.close_devices()


# command run arguments to unmount the drive

# subprocess.run(umount_cmd)