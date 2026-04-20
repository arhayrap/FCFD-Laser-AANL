import subprocess
import os


# directories/paths to files
sh_script_path = "/home/cmspractice/FCFD-Project/FCFD-Laser-main/DAQ/TimingDAQ_mod/script_FCFD.sh"
BASE_PATH = "/home/cmspractice/FCFD-Project/FCFD-Laser-main/DAQ" # this is for the file indexing txt file

def GetNextNumber():
    run_num_file = BASE_PATH + "/next_run_number.txt"
    FileHandle = open(run_num_file)
    nextNumber = int(FileHandle.read().strip())
    FileHandle.close()
    FileHandle = open(run_num_file,"w")
    FileHandle.write(str(nextNumber+1)+"\n") 
    FileHandle.close()
    return nextNumber

# the range of runs
start_index = 1
end_index = 5

# writes the starting run number intor the next_run_number.txt file
# run_num_file = BASE_PATH + "/next_run_number.txt"
# FileHandle = open(run_num_file)
# nextNumber = int(FileHandle.read().strip())
# FileHandle.close()
# FileHandle = open(run_num_file,"w")
# FileHandle.write(str(start_index)+"\n") 
# FileHandle.close()


# # pre-processes the runs from start_index to end_index
# for i in range(start_index, end_index + 1):  # start_index to end_index inclusive
#     try:
#         latest_run_number = str(GetNextNumber())
#         subprocess.run(["bash", sh_script_path, latest_run_number], check=True)
#         print("DAQ pipeline ok.")

#     except Exception as e:
#         print(f"shell hook failed: {e}")



for latest_run_number in range(1, 6):

    try:
        latest_run_number = str(latest_run_number)
        subprocess.run(["bash", sh_script_path, latest_run_number], check=True)
        print("DAQ pipeline ok.")

    except Exception as e:
        print(f"shell hook failed: {e}")