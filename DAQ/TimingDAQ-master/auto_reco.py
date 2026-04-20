import time
import numpy as np
import getpass
import os
import subprocess as sp
import socket
import sys
import glob
import subprocess
from subprocess import Popen, PIPE
import pipes 
from pipes import quote
import argparse

def check(list_to_check):
    bool = True
    for element in list_to_check:
        if not element.isdigit():
             print 'Removing %s element in the list' % element
             list_to_check.remove(element)
             bool = False
    return bool, list_to_check

def exists_remote(host, path):
    """Test if a file exists at path on a host accessible with SSH."""
    #print pipes.quote(path)
    status = subprocess.call(['ssh', host, 'test -f {0}'.format(pipes.quote(path))])
    if status == 0:
        return True
    if status == 1:
        return False
    raise Exception('SSH failed')

def errorfile(run_number, error):
    errorfile_handle = open("/home/daq/fnal_tb_18_11/ErrorLog/run_%d.txt" % run_number, "a+") 
    errorfile_handle.write("Error.............." + error + "\n \n \n")
    errorfile_handle.close()

def readfile(filepath):
    RunFile = open(filepath)
    NextRunNumber = int(RunFile.read().strip())
    RunFile.close()
    return NextRunNumber
    

#####################Parsing arguments###################
                                                                                                                               
parser = argparse.ArgumentParser(description='Information for running the automated reconstruction program')
parser.add_argument('-d', '--Digitizer', type=str, default = 'NetScopeStandalone', help='Give NetScopeStandalone or DT5742 or VME', required=False)
parser.add_argument('-v', '--Version', type=str, default = 'v3', help='Version of the configuration', required=False)
parser.add_argument('-w', '--SaveWaveform', type=int, default = 1, required=False)
parser.add_argument('-t', '--WannaTrack', type=int, default=0, required=False)
parser.add_argument('-r', '--RunNumber', type=int, help = 'It will start the processing from this run number',required=True)
parser.add_argument('-mr', '--MaxRunNumber', type=int, help = 'Maximum run number',required=True)
parser.add_argument('-nr', '--ScopeNextRunNumberFrom', type=int, default= 0, help = 'It will read the next run number from this text file. If using OTSDAQ use 1 else use 0',required=False)
parser.add_argument('-k', '--KillTime', type=int, default = 0, help = 'Enable 2s process kill time after each run.',required=False)
parser.add_argument('-lrn', '--LastRunNumber', type=int, default = 1, help = 'Having this bool enabled will let this program do the reco for last run number (read from run text file - 1) as well.',required=False)

args = parser.parse_args()
RunNumber = args.RunNumber
Digitizer = args.Digitizer
Version = args.Version
SaveWaveformBool = args.SaveWaveform
WannaTrack = args.WannaTrack 
ScopeNextRunNumberFrom = args.ScopeNextRunNumberFrom
KillTimeBool = args.KillTime
MaxRunNumber = args.MaxRunNumber
LastRunNumber = args.LastRunNumber


##################Hard Code these paths#####################

if Digitizer == 'NetScopeStandalone':
    RawLocalPath = '/home/daq/fnal_tb_18_11/LocalData/ROOT/'
    RawLocalPath2 = '/home/daq/fnal_tb_18_11/ScopeMount/'
else:
    RawLocalPath = '/home/daq/fnal_tb_18_11/' +  Digitizer + '/' 
RecoLocalPath = '/home/daq/fnal_tb_18_11/LocalData/RECO/' + Digitizer + '/' + Version + '/'
BaseTrackDirRulinux = '/data/TestBeam/2018_11_November_CMSTiming/'
BaseTrackDirLocal = '/home/daq/fnal_tb_18_11/Tracks/'
HyperscriptPath = '/home/otsdaq/CMSTiming/HyperScriptFastTrigger_NewGeo_18_12_11.sh'
ConfigFilePath = '/home/daq/TimingDAQ/config/FNAL_TestBeam_1811/' + Digitizer + '_%s.config' % Version
EnvSetupPath = '/home/daq/otsdaq/setup_ots.sh'
RulinuxSSH = 'otsdaq@rulinux04.dhcp.fnal.gov'
LocalSSH = 'daq@timingdaq02.dhcp.fnal.gov'
TimingDAQDir = '/home/daq/TimingDAQ/'
ScopeRecoCMD1 = 'python /home/daq/fnal_tb_18_11/Tektronix_DPO7254Control/Reconstruction/conversion.py /home/daq/fnal_tb_18_11/ScopeMount/run_scope'
NextRunNumberFile = 'otsdaq_runNumber.txt' if ScopeNextRunNumberFrom == 1 else 'runNumber.txt'  
ScopeNextRunNumberPath = '/home/daq/fnal_tb_18_11/Tektronix_DPO7254Control/RunOscilloscope/' + NextRunNumberFile



################ Check if the above defined path exist############

if not os.path.exists(ConfigFilePath): print '\n Configuration file doesnt exist for the version %s at %s  \n' % (Version,ConfigFilePath)
if not os.path.exists(RecoLocalPath): os.system('mkdir %s' % RecoLocalPath)


def TrackFileRemoteExists(x):
    TrackFilePathRulinux = BaseTrackDirRulinux +'CMSTimingConverted/Run%i_CMSTiming_converted.root' % x
    return exists_remote(RulinuxSSH, TrackFilePathRulinux)

def TrackFileLocalExists(x): 
    TrackFilePathLocal = BaseTrackDirLocal + 'Run%i_CMSTiming_converted.root' % x
    return os.path.exists(TrackFilePathLocal)


if Digitizer == 'NetScopeStandalone': 

    while True:
                    #First stage reco for the scope
                    list_raw_stage1 = [(x.split("run_scope")[1]) for x in glob.glob(RawLocalPath2 + 'run_*')]
                    list_reco_stage2 = [(x.split("run_scope")[1].split("_converted.root")[0]) for x in glob.glob(RecoLocalPath + 'run_*')] #run_scope398.root 
                    list_reco_stage1 = [(x.split("run_scope")[1].split(".root")[0]) for x in glob.glob(RawLocalPath + 'run_*')]

                    #sets containing run numbers from raw folder and reco folder                                                                               
                    set_raw_stage1 = set([int(x) for x in list_raw_stage1])
                    set_reco_stage2 = set([int(x) for x in list_reco_stage2])
                    set_toreco_stage1and2 = set_raw_stage1 - set_reco_stage2

                    if len(set_toreco_stage1and2) == 0:
                        print '\n ###################### NO RUNS TO PROCESS ####################### \n'

                    else:
 
                        for x in set_toreco_stage1and2:       

                            RecoStage2Ready = False
                            TrackReady = False
                            BadScpOrTrack = False
                            NextRunNumber = readfile(ScopeNextRunNumberPath)
                            if not LastRunNumber: NextRunNumber = NextRunNumber - 1
                            TrackFilePathRulinux = BaseTrackDirRulinux +'CMSTimingConverted/Run%i_CMSTiming_converted.root' % x
                            TrackFilePathLocal = BaseTrackDirLocal + 'Run%i_CMSTiming_converted.root' % x
                            SCPTrackCMD = 'scp ' + TrackFilePathRulinux + ' ' + LocalSSH + ':' + BaseTrackDirLocal
                            abs_raw2_file_path = RawLocalPath + 'run_scope' + str(x) + '.root'
                            abs_reco2_file_path = RecoLocalPath + 'run_scope' + str(x) + '_converted.root'
                            

                            ##########################RECO_STAGE1#######################

                            # Read the run number from this text file and only if it is > x+1, then do reco1 for x
                            if x < NextRunNumber and x >= RunNumber and x <= MaxRunNumber:

                                print '############################ RUN NUMBER %i ############################' % x
                            
                                if str(x) not in list_reco_stage1:
                                    session1 = subprocess.Popen('source %s; %s' % (EnvSetupPath,ScopeRecoCMD1 + str(x)),stdout=PIPE, stderr=PIPE, shell=True)
                                    stdout, stderr = session1.communicate()
                                    if stderr:
                                        print '\n Reco first stage threw some error. Not Doing the further Processing.  \n'
                                        errorfile(x,"RECO1" + str(stderr))
                                        RecoStage2Ready = False
                                        WannaTrack = False
                                    else:
                                        print '\n Reco first stage successful.  \n'
                                        RecoStage2Ready = True
                                else:
                                    print '\n Reco first stage output file is already present.  \n'
                                    RecoStage2Ready = True

                                                                    
                                ##################Tracking################
                                if WannaTrack:

                                    #################Tracking Status####################
                                    if TrackFileRemoteExists(x) and TrackFileLocalExists(x):
                                        print '\n Track file exist and is already present locally \n' 
                                        RecoStage2Ready = True
                                    elif TrackFileRemoteExists(x):
                                        print '\n Track file exist on RULinux but not locally, copying Track file to remote computer \n'
                                        os.system(SCPTrackCMD)
                                        BadScpOrTrack = not TrackFileLocalExists(x)
                                        RecoStage2Ready = True
                                    elif not TrackFileRemoteExists(x):
                                        TrackReady = True
        

                                    #################Doing Tracking######################
                                    if TrackReady:
                                        print '\n Doing Tracking \n'
                                        session = subprocess.Popen(["ssh", RulinuxSSH, ". " + HyperscriptPath + " %i" % x], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                                        stdout, stderr = session.communicate()
                                        if stderr:
                                            BadScpOrTrack = True
                                            errorfile(x, "Tracking")
                                            print '\n Tracking threw an error \n'
                                            if TrackFileRemoteExists(x) and  not TrackFileLocalExists(x):
                                                print '\n The error was due to a problem in SCPing from rulinux to local machine \n \n Not doing the Tracking now \n'
                                            elif not TrackFileRemoteExists(x) and  not TrackFileLocalExists(x):
                                                print '\n The error was an intrinsic Tracking error \n'
                                                errorfile(x, "Intrinsic Tracking")                                    
                                            else:
                                                print "\n Tracking didn't throw any error \n" 
                                                #Checking if the track file now exists on rulinux    
                                                if TrackFileLocalExists(x) and TrackFileRemoteExists(x):
                                                    print '\n Track file now exists on rulinux and locally \n'

                                    #################Tracking Size######################
                                    if not BadScpOrTrack: 
                                        RecoStage2Ready = True
                                        print '\n Checking Tracking file size on local machine \n'
                                        statinfo = os.stat(TrackFilePathLocal)
                                        if statinfo.st_size < 10000:
                                            BadScpOrTrack = True
                                            print '\n The track file size is too small, tracking was bad. \n'
                                            errorfile(x, "SMALL TRACKING FILE")
                                        else:    
                                            print '\n The track file size is fine, Doing the reco \n'



                                #####################RECO_STAGE2######################
                                if RecoStage2Ready:

                                    dattoroot_cmd = './' + Digitizer + 'Dat2Root' + ' --config_file=' + ConfigFilePath + ' --input_file=' + abs_raw2_file_path + ' --output_file=' + abs_reco2_file_path
                                    if SaveWaveformBool: dattoroot_cmd = dattoroot_cmd + ' --save_meas'
                                    if WannaTrack and not BadScpOrTrack and TrackFileLocalExists(x): dattoroot_cmd = dattoroot_cmd + ' --pixel_input_file=' + TrackFilePathLocal 
                                    elif WannaTrack and BadScpOrTrack or not TrackFileLocalExists(x):
                                        print '\n Tracking file does not exist on the local machine or is not wanted, Doing the reco without tracking \n'
                                    
                                    #Doing the reco stage 2
                                    session2 = subprocess.Popen('cd %s; source %s; %s;cd -' % (TimingDAQDir,EnvSetupPath,dattoroot_cmd),stdout=PIPE, stderr=PIPE, shell=True)
                                    stdout, stderr = session2.communicate()

                                    if stderr:
                                        print '\n Reco threw some error \n'
                                        errorfile(x, "RECO" + str(stderr))

                                print '############################ DONE WITH RUN NUMBER %i ############################' % x
                                print '\n \n \n \n'
                                if KillTimeBool: time.sleep(2)

                    print 'Going to sleep for 20 seconds...................'
                    time.sleep(20)











if Digitizer == 'DT5742' or Digitizer == 'VME': 

    while True:

                list_raw_to_check = [(x.split("_Run")[1].split(".dat")[0].split("_")[0]) for x in glob.glob(RawLocalPath + '*_Run*')]
                list_reco = [(x.split("_Run")[1].split(".root")[0].split("_")[0]) for x in glob.glob(RecoLocalPath + '*_Run*')]

                abs_raw_file_path_list = [x for x in glob.glob(RawLocalPath + '*_Run*')] 
                abs_reco_file_path_list = [x for x in glob.glob(RecoLocalPath + '*_Run*')]                 
                
                #Check if the list is fine                                                                                                                                                                                                   
                bool, list_raw = check(list_raw_to_check)
                if(bool):
                    print '\n The Filenames in the list are fine. \n'
                else:
                    print '\n Filenames in the list are screwed up, not processing bad file names!!!!!!!!!!!!!! \n'
                time.sleep(5)

                #sets containing run numbers from raw folder and reco folder                                                                                                                                                        
                set_raw = set([int(x) for x in list_raw])
                set_reco = set([int(x) for x in list_reco])
                set_toprocess = set_raw - set_reco
                if len(set_toprocess) == 0:
                        print '\n ###################### NO RUNS TO PROCESS ####################### \n'
                        

                for x in set_toprocess:                    
                    BadScpOrTrack = False
                    if x >= RunNumber:
                        #Check if the track is already there
                        print '############################ RUN NUMBER %i ############################' % x
                        TrackFilePathRulinux = BaseTrackDirRulinux +'CMSTimingConverted/Run%i_CMSTiming_converted.root' % x
                        TrackFilePathLocal = BaseTrackDirLocal + 'Run%i_CMSTiming_converted.root' % x
                        if exists_remote(RulinuxSSH, TrackFilePathRulinux):
                            if os.path.exists(TrackFilePathLocal):
                                print '\n Track file exist and is already present locally, no need to do Tracking or copying \n' 
                            else:
                                print '\n Track file exist on rulinux but not locally, copying Track file \n'
                                copy_cmd = 'scp ' + TrackFilePathRulinux + ' ' + LocalSSH + ':' + BaseTrackDirLocal
                                os.system(copy_cmd)
                            BadScpOrTrack = not os.path.exists(TrackFilePathLocal)
                        elif WannaTrack:
                            print '\n Doing Tracking \n'
                            #Doing the tracking for the run
                            session = subprocess.Popen(["ssh", RulinuxSSH, ". " + HyperscriptPath + " %i" % x], stderr=subprocess.PIPE, 
                            stdout=subprocess.PIPE)
                            #print ["ssh", RulinuxSSH, ". " + HyperscriptPath + " %i" % x]
                            stdout, stderr = session.communicate()
                            if stderr:
                                BadScpOrTrack = True
                                errorfile(x, "Tracking")
                                print '\n Tracking threw an error \n'
                                if exists_remote(RulinuxSSH, TrackFilePathRulinux) and  not os.path.exists(TrackFilePathLocal):
                                    print '\n The error was due to a problem in SCPing from rulinux to local machine \n \n Not doing the Tracking now \n'
                                elif not  exists_remote(RulinuxSSH, TrackFilePathRulinux) and  not os.path.exists(TrackFilePathLocal):
                                    print '\n The error was an intrinsic Tracking error \n'
                                    errorfile(x, "Intrinsic Tracking")                                    
                            else:
                                print "\n Tracking didn't throw any error \n" 
                                #Checking if the track file now exists on rulinux    
                                if exists_remote(RulinuxSSH, TrackFilePathRulinux) and os.path.exists(TrackFilePathLocal):
                                    print '\n Track file now exists on rulinux and locally \n'

                        #Checking Track file size
                        if not BadScpOrTrack: 
                                if WannaTrack:
                                    print '\n Checking Tracking file size on remote machine \n'
                                    statinfo = os.stat(TrackFilePathLocal)
                                    if statinfo.st_size < 10000:
                                        print '\n The track file size is too small, tracking was bad: not doing the reco \n'
                                        errorfile(x, "SMALL TRACKING FILE")
                                    else:    
                                        print '\n The track file size is fine, Doing the reco \n'

                                
                                #Constructing the reco command
                                abs_raw_file_path = abs_raw_file_path_list[list_raw_to_check.index(str(x))]
                                abs_reco_file_path = RecoLocalPath + Digitizer + '_RECO_Run' + str(x) + '.root'
                                #abs_reco_file_path = abs_reco_file_path_list[list_reco.index(str(x))]

                                if SaveWaveform:
                                    dattoroot_cmd = './' + Digitizer + 'Dat2Root' + ' --config_file=' + ConfigFilePath + ' --save_meas' + ' --output_file=' + abs_reco_file_path
                                else:
                                    dattoroot_cmd = './' + Digitizer + 'Dat2Root' + ' --config_file=' + ConfigFilePath + ' --output_file=' + abs_reco_file_path

                                if WannaTrack:
                                    dattoroot_cmd = dattoroot_cmd + ' --pixel_input_file=' + TrackFilePathLocal

                                if Digitizer == 'NetScopeStandalone':
                                    dattoroot_cmd = dattoroot_cmd + ' --input_file=' + abs_raw_file_path
                                    reco_cmd1 = 'python /home/daq/fnal_tb_18_11/Tektronix_DPO7254Control/Reconstruction/run_conversion.py -r %d' % RunNumber
                                    session1 = subprocess.Popen(reco_cmd1,stdout=PIPE, stderr=PIPE, shell=True)
                                    stdout, stderr = session1.communicate()
                                    if stderr:
                                        print '\n Reco first stage threw some error \n'
                                        errorfile(x,"RECO1" + str(stderr))

                                session2 = subprocess.Popen('cd %s; source %s; %s;cd -' % (TimingDAQDir,EnvSetupPath,dattoroot_cmd),stdout=PIPE, stderr=PIPE, shell=True)
                                stdout, stderr = session2.communicate()

                                if str(stderr) == str("VMEDat2Root: app/VMEDat2Root.cc:22: int main(int, char**): Assertion `false' failed."):
                                    print '\n The reco was fine \n'
                                elif stderr and str(stderr) != "VMEDat2Root: app/VMEDat2Root.cc:22: int main(int, char**): Assertion `false' failed.":
                                    print '\n The reco threw some error \n'
                                    errorfile(x, "RECO" + str(stderr)) 
                        else:
                            print '\n There was an error in SCPing from RULINUX to local machine \n \n Not doing the Tracking now \n'
                            errorfile(x, "SCP from RULINUX to Local Machine")
                        print '############################ DONE WITH RUN NUMBER %i ############################' % x
                        print '\n \n \n \n'
                
                print 'Going to sleep for 20 seconds...................'
                time.sleep(20)

