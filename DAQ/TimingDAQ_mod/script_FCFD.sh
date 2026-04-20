#!/bin/bash

# cp /home/arcadia/Documents/Motors_automation_test/DAQtest/Converted_runs_root/converted_run$1.root .

# for raw data + root
# /home/arcadia/Documents/Motors_automation_test/TimingDAQ/NetScopeStandaloneDat2Root --input_file=/home/arcadia/Documents/Motors_automation_test/DAQtest/Converted_runs_root/converted_run$1.root --config=/home/arcadia/Documents/Motors_automation_test/TimingDAQ/LecroyScope_v11.config --output_file=/home/arcadia/Documents/Motors_automation_test/DAQtest/Preprocessed_runs_root/out_run$1.root --correctForTimeOffsets=true

# # only for root (without raw data)
# /home/cmspractice/FCFD-Project/FCFD-Laser-main/DAQ/TimingDAQ_mod/NetScopeStandaloneDat2Root --input_file=/home/cmspractice/FCFD-Project/FCFD-Laser-main/DAQ/Converted/converted_run$1.root --config=/home/cmspractice/FCFD-Project/FCFD-Laser-main/DAQ/TimingDAQ_mod/LecroyScope_v11.config --output_file=/home/cmspractice/FCFD-Project/FCFD-Laser-main/DAQ/PreProcessed/out_run$1.root --correctForTimeOffsets=true

# # -------------- for cmspractice PC ------------------ (saving raw data too)
# /home/cmspractice/FCFD-Project/FCFD-Laser-main/DAQ/TimingDAQ-master/NetScopeStandaloneDat2Root --input_file=/home/cmspractice/FCFD-Project/FCFD-Laser-main/DAQ/Converted/converted_run$1.root --config=/home/cmspractice/FCFD-Project/FCFD-Laser-main/DAQ/TimingDAQ_mod/LecroyScope_v11.config --output_file=/home/cmspractice/FCFD-Project/FCFD-Laser-main/DAQ/PreProcessed/out_run$1.root --correctForTimeOffsets=true


# # -------------- for cmspractice PC ------------------ (without saving the raw data)

/home/cmspractice/FCFD-Project/FCFD-Laser-main/DAQ/TimingDAQ-master/NetScopeStandaloneDat2Root --input_file=/home/cmspractice/FCFD-Project/FCFD-Laser-main/DAQ/Converted/converted_run$1.root --config=/home/cmspractice/FCFD-Project/FCFD-Laser-main/DAQ/TimingDAQ_mod/LecroyScope_v11.config --output_file=/home/cmspractice/FCFD-Project/FCFD-Laser-main/DAQ/PreProcessed/out_run$1.root --correctForTimeOffsets=true --save_meas=false


# cp out_run$1.root /home/arcadia/Documents/Motors_automation_test/DAQtest/Preprocessed_runs_root
# rm *$1*.root
