import numpy as np
import matplotlib.pyplot as plt
'''
Laser:
50Hz, 2% and 10% pulse width
'''
# Laser firing frequency is 50 Hz (pulse frequency)
# 

Bias_Voltage = [0, 2.5, 5, 7.5, 10, 12.5, 15, 17.5, 20] #V

Amplitude_2 = [0.6, 0.2, 0.15, 0.1, 0.1, 0.075, 0.05, 0.05, 0.04] #V
Amplitude_2 = np.array(Amplitude_2) / 2.5 
# divided by 2.5 because a knob on the scope had scaled the units
Bias_Voltage_2 = Bias_Voltage[:len(Amplitude_2)]

Amplitude_10 = [0.3, 0.1, 0.05, 0.05, 0.04, 0.04, 0.04, 0.03, 0.03]
Amplitude_10 = np.array(Amplitude_10)
Bias_Voltage_10 = Bias_Voltage[:len(Amplitude_10)]

Amplitude_50 = [0.15, 0.06, 0.04, 0.035, 0.03, 0.03, 0.03, 0.025, 0.02]
Amplitude_50 = np.array(Amplitude_50)
Bias_Voltage_50 = Bias_Voltage[:len(Amplitude_50)]


plt.plot(Bias_Voltage_2, Amplitude_2, marker = 'x', label = 'PW = 2%')
plt.plot(Bias_Voltage_10, Amplitude_10, marker = 'x', label = 'PW = 10%')
plt.plot(Bias_Voltage_50, Amplitude_50, marker = 'x', label = 'PW = 50%')
plt.grid()
plt.legend()
plt.title("Bias Voltage VS Signal Amplitude")
plt.xlabel("Bias Voltage Given to the Diode [V]")
plt.ylabel("Amplitude Measured by the Oscillograph [V]")
plt.show()