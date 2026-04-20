import subprocess

# BASE_PATH = "/home/arcadia/Documents/Motors_automation_test/DAQtest"

# def WriteNextNumber():
    
#     run_num_file = BASE_PATH + "/next_run_number.txt"
#     FileHandle = open(run_num_file)
#     nextNumber = int(FileHandle.read().strip())
#     FileHandle.close()
#     FileHandle = open(run_num_file,"w")
#     FileHandle.write(str(nextNumber+1)+"\n") 
#     FileHandle.close()


start_index = 1
end_index = 5


for i in range(start_index, end_index + 1):  # 2 to 184 inclusive
    print(f"Running conversion.py for index {i}")
    result = subprocess.run(["python", "/home/cmspractice/FCFD-Project/FCFD-Laser-main/DAQ/conversion.py", "--runNumber", str(i)])

    if result.returncode != 0:
        print(f"conversion.py failed for index {i}")
    else:
        print(f"Finished index {i}")

    # WriteNextNumber()
