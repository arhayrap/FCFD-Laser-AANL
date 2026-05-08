# FCFD-Laser

### Use the motors to control X, Y and Z positions of the table and the lens.

Move to DAQ directory:
```
cd DAQ
python3 motortools_v2-1.py
```
To move the position of the table (X, Y) and the lens (Z) use the following commands:
```
daN - Moves in 'a' axis direction (x/y/z) by 'N' microns.
aN - Goes to coordinate 'N' on 'a' axis.
hN - Moves to 'N'th predefined home coordinate.
pos - Print current position.
```
where a - is the name of the axis to control (x, y, z).

### Run the watchdog, to perform DQM during measurements.
```
cd watchdog
python3 watchdog_treev11.py
```
This will display amplitudes, timestamps and fitted measured $\Delta T$ distribution.

# Main DAQ scripts

So-called "Main DAQ" scripts are
[acquisition.py](#acquisitionpy),
[constants.py](#constantspy),
[conversion.py](#conversionpy),
[logger.py](#loggerpy),
[motortools_v2-1.py](#motortools_v2-1py),
[MOVE_DAQ_CONVERSTION.py](#move_daq_converstionpy).

---

## ```acquisition.py```

### **What this script does.**
This code establishes connection between the LECROY Scope and the control PC. From PC, it sends commands to the Scope, which starts the data acquisition. After finishing acquiring data from that certain point, the Scope saves the raw data in .trc format. After that, the PC copies the raw data files to its local storage.

### **Explanation of some important lines of code (note that these lines should be adjusted to every setup):**
```python
LECROY_IP = "192.168.0.170"
```

You should assign IPs to the PC and Scope to establish an ethernet connection between the two. Make sure you have the IPs right.

```python
BASE_PATH = "/home/arcadia/Documents/Motors_automation_test/DAQtest"

run_log_path = BASE_PATH + "/RunLog.txt"
```
The first line is the base path (FCFD-Laser path), and the second line is the path for a log file, where the errors of the script will be saved.

```python
NSegments = 100
```
These are the acquired segments per run. A segment is the same as an event (the single signal graph is a segment). Each segment consists of 20000 samples (sample is a point on the graph). This means that if we use 8 channels to acquire data, one event will be described with 20000 * (8 + 1)  = 180 000 numbers (8-amplitudes from 8 channels, +1 is for the time axis).



## ```constants.py```

### **What this script does.**
Even though this script is not fully integrated in the project, the final goal of it is to store all globally used variables in one single small script. This means that variables such as Scope and PC IP addresses, project base paths, number of segments per run, board docking home coordinates and similar parameters should eventually be changed only from this file.

### **Explanation of some important lines of code (note that these lines should be adjusted to every setup):**
```python
LECROY_IP = "192.168.0.170"
```
This line defines the IP address of the Scope. Make sure that the IP corresponds to the actual Scope IP configured in your local network.

```python
BASE_PATH = "/home/arcadia/Documents/Motors_automation_test/DAQtest"
```
This line defines the main project path (FCFD-Laser directory). All other paths are usually constructed relative to this directory.

```python
NSegments = 100
```
This line defines the number of acquired segments (events) per run.

```python
HOME_X = 0
HOME_Y = 0
HOME_Z = 0
```
These lines define the docking (home) coordinates of the board and the lens system.

### **Common issues and how to resolve them.**
There are no known issues with this script yet. Most problems come from entering incorrect paths, coordinates or IP addresses.


## ```conversion.py```

### **What this script does.**
This script converts the raw data copied from the Scope into a ROOT file. In general, this script does not process the data. You can think of this step as combining all 8 raw data `.trc` files into one large ROOT file that is easier to process later.

### **Explanation of some important lines of code (note that these lines should be adjusted to every setup):**
```python
RawDataPath = "/home/arcadia/Documents/Motors_automation_test/DAQtest"
```
This line defines the path to the folder where the raw data copied from the Scope is stored.

```python
OutputFilePath = BASE_PATH + "/Converted_runs_root"
```
This line defines where the converted ROOT files will be saved.

```python
NChannels = 8
```
This line defines the number of channels used during data acquisition. Make sure this value corresponds to the actual number of Scope channels used during the measurement.

### **Common issues and how to resolve them.**
One common issue is incorrect file paths. Make sure that:
- the raw `.trc` files exist in the specified input directory,
- the output directory exists,
- and the script has permission to read and write files.

Another possible issue is mismatching number of channels. Be sure that the configured number of channels matches the acquired data.


## ```logger.py```

### **What this script does.**
This script is responsible for logging messages, warnings and errors produced during DAQ operation. The goal of this script is to simplify debugging by saving important runtime information into log files.

### **Explanation of some important lines of code (note that these lines should be adjusted to every setup):**
```python
run_log_path = BASE_PATH + "/RunLog.txt"
```
This line defines the location of the main log file where runtime information and errors will be stored.

```python
with open(run_log_path, "a") as logfile:
```
This line opens the log file in append mode. This means that new messages will be added to the end of the file without deleting previous logs.

### **Common issues and how to resolve them.**
One possible issue is incorrect file permissions. Make sure the script has permission to create and modify the log file.

Another issue may appear if the base path does not exist. Verify that the `BASE_PATH` variable is correct.


## ```motortools.py```

### **What this script does.**
This script provides full manual control over the motors (=> the board). There are several modes/commands you can use:
- `s` for step mode,
- `c` for coordinate mode,
- `h` for docking to home coordinates,
- `*` for exiting the mode or the script.

You can choose the desired mode right after running the script.

In step mode:
1. choose an axis (`x`, `y` or `z`),
2. enter the step length in microns,
3. repeat or exit using `*`.

Negative numbers can also be entered. In this case the board will move in the opposite direction.

In coordinate mode:
1. choose an axis,
2. enter the coordinate you want to move to,
3. repeat or exit using `*`.

Unlike step mode, coordinate mode moves the board to an absolute coordinate rather than moving it by a relative distance.

Sending the `h` command docks the board to predefined home coordinates. These coordinates can be changed in `motortools.py` and/or `constants.py`.

Typing `*` exits the current mode or the entire script.

### **Explanation of some important lines of code (note that these lines should be adjusted to every setup):**
```python
def __init__(self,
             Motor_X = r"xi-com:///dev/ttyACM2",
             Motor_Y = r"xi-com:///dev/ttyACM0",
             Motor_Z = r"xi-com:///dev/ttyACM1",
             ):
```
These lines define the three motors corresponding to the X, Y and Z axes.

The PC recognizes the motors as separate USB devices, even though only one USB cable may be connected to the controller system. Make sure that the software-defined axes correspond to the correct physical axes on the hardware.

If necessary, you can swap the last numbers (`0`, `1`, `2`) in `ttyACM0`, `ttyACM1`, `ttyACM2` until the axes are assigned correctly.

### **Common issues and how to resolve them.**
```python
libximc.highlevel
```
This Python library must be installed for motor communication. Installation instructions can be found on the official website.

Sometimes the PC may fail to recognize the motors. In this case try unplugging and reconnecting the USB cable.

Another common issue is incorrect axis assignment. If the X, Y and Z axes move incorrectly, adjust the `ttyACM` device numbers.


## ```MOVE_DAQ_CONVERSION.py```

### **What this script does.**
This script is the final automated DAQ script as of August 29th.

First, you should manually position the laser to the desired starting point. After running the script, it will ask:
- how many steps should be taken in X and Z directions,
- and the sizes of the X and Z steps (`move_X` and `move_Z`).

After entering these parameters, the script will:
1. acquire data from the Scope,
2. convert the raw data,
3. preprocess the data,
4. and save the results on the PC local storage.

### **Important note about optimization**
This script is not optimized. Its main loop is essentially:
```text
acquisition.py -> conversion.py -> script_FCFD.sh -> acquisition.py
```

This means that after the Scope finishes acquiring data from point `N`, it waits until:
- conversion is finished,
- preprocessing is finished,
- and only then starts acquisition from point `N+1`.

During this waiting time the laser may continue heating the board. Because of this, the script should mainly be used for small scans or as a temporary solution.

### **Explanation of some important lines of code (note that these lines should be adjusted to every setup):**
```python
sh_script_path = ".../TimingDAQ/script_FCFD.sh"
```
This line defines the path to the shell script responsible for running the preprocessing code.

### **Common issues and how to resolve them.**
This script combines multiple DAQ stages together, so failures may come from:
- acquisition,
- conversion,
- preprocessing,
- motor movement,
- or incorrect file paths.

In general, the script should eventually be redesigned and optimized for stable automated DAQ operation.


## ```motortools_v2-1.py```

### **What this script does.**
This script is an improved version of the motor control software designed for easier and faster manual adjustment of the board position.

Unlike the older `motortools.py`, this version uses a simplified command system similar to G-code commands. This allows the user to move the board and lens system directly from the terminal using short text commands.

The script supports:
- relative movements,
- absolute coordinate movements,
- predefined home coordinates,
- command sequences,
- and current position monitoring.

### **Available commands**
```text
dx100
```
Moves 100 microns in positive `x` direction.

```text
dy-200
```
Moves 200 microns in negative `y` direction.

```text
z100
```
Moves the system so the new absolute `z` coordinate becomes `100`.

```text
x-300
```
Moves the system so the new absolute `x` coordinate becomes `-300`.

```text
h1
```
Moves the board to the first predefined home coordinate.

Similarly:
```text
h2, h3, ..., hN
```
move to other predefined home coordinates.

```text
*
```
or
```text
q
```
Exits the script.

```text
pos
```
Prints the current motor coordinates.

### **Sending multiple commands**
You can also send multiple commands at once:

```text
dx100 y-200 z400 h2
```

This sequence will:
1. move `x` by `+100` microns,
2. move to absolute `y = -200`,
3. move to absolute `z = 400`,
4. and finally move to the second predefined home coordinate.

### **Explanation of some important lines of code (note that these lines should be adjusted to every setup):**
```python
Motor_X = r"xi-com:///dev/ttyACM2"
Motor_Y = r"xi-com:///dev/ttyACM0"
Motor_Z = r"xi-com:///dev/ttyACM1"
```
These lines define which USB motor devices correspond to the X, Y and Z axes.

Make sure that the software-defined axes correspond to the correct physical axes on the hardware. If necessary, swap the `ttyACM` numbers.

```python
home_coordinates = [
        [-2000, -2000, -2000],   # RED laser
        [-2000, -2000, -2000],   # IR laser
        [-2000, -19000, -52000],   # March 20 scan
        # [46105, 35000,     0],   # h4 — SIG1 strip (alt)
        # [50400, 40000,     0],   # h5 — FCFD 1.1 (alt)
```
This lines define several home coordinates. If you want to go to the ```[-2000, -19000, -52000]```, for example, just type in ```h3``` in the terminal.

### **Common issues and how to resolve them.**
One common issue is incorrect motor-to-axis assignment. If the wrong axis moves, change the corresponding `ttyACM` device numbers.

Another possible issue is that the motors are not recognized by the PC. In this case:
- unplug the USB cable,
- reconnect it,
- and restart the script.

Be sure that the required motor control libraries (for example `libximc.highlevel`) are installed correctly.