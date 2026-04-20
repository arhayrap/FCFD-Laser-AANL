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

### 