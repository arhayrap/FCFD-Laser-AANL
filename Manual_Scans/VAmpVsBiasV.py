import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

'''
Scope - Tektronix TDS 2012
100MHz, 1GS/s

Laser Pulse Frequency = 50Hz
Laser - Particulars Laser (IR)
Focused beamspot - unknown ?
No Bias Voltage
'''

voltage_amplitude = [11.2, 17.6, 20.4, 20.8, 21.6, 22.4, 23.6, 22.8, 24.0, 24.4, 25.2, 26.0, 26.8, 27.2, 28.0, 28.8, 29.2, 30.4, 30.8, 31.6, 32.0] # Voltage amplitude at which 50 Hz signal frequency is observed.
n_points = len(voltage_amplitude)
bias_voltage = np.linspace(0,n_points-1,n_points)

print(bias_voltage)
print(len(bias_voltage), len(voltage_amplitude))

plt.plot(bias_voltage, voltage_amplitude, marker = "o")
# plt.legend()
plt.title('Bias voltage scan (pulse f = 50Hz)')
plt.xlabel('Bias voltage [V]')
plt.ylabel('Trigger level [V]')
plt.grid()
plt.show()
