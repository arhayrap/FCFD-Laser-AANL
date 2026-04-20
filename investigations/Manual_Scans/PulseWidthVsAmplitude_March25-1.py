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

def hyperbola_model(x, a, b, c):
    return a/(x+c) + b


# 'vd' for voltage drop
vd_1 = [20.0, 18.8, 18.4, 18.0, 16.8, 
        14.0, 7.0, 6.4, 5.6, 5.2,
        4.2, 4.8, 4.72, 4.4, 3.5,
        2.7, 2.16, 1.84, 1.44, 1.4,
        0
]

vd_2 = [5.8, 5.0, 3.6, 3.4, 3.0,
        2.6, 2.0, 2.6, 1.76, 1.0, 0.64]

#converting to numpy arrays
vd_1 = np.array(vd_1)
vd_2 = np.array(vd_2)

# 'pw' for pulse width
pw_1 = np.linspace(0, 100, len(vd_1))
pw_2 = np.linspace(0, 100, len(vd_2))

# Preparing the fit
popt, pcov = curve_fit(hyperbola_model, pw_2, vd_2)

a_fit = popt[0]
b_fit = popt[1]
print(f"Optimal parameters: a = {a_fit}, b = {b_fit}")


x_fit = np.linspace(min(pw_2), max(pw_2), 100) # Range for smooth plot
y_fit = hyperbola_model(x_fit, *popt)


plt.plot(x_fit, y_fit, 
         color='green',
         label='Fitted function',
        #  marker='o'
         )


# plt.plot(pw_1, vd_1, 
#          color='blue',
#          label='Initial scan',
#          marker='o'
#          )


plt.plot(pw_2, vd_2, 
         color='red',
         label='Revisited scan',
         marker='o'
         )




plt.legend()

plt.title('Pulse Width Scan (pulse f = 50Hz)')
plt.xlabel('Pulse Width [%]')
plt.ylabel('Voltage Drop [V]')
plt.grid()

plt.savefig('/home/cmspractice/FCFD-Project/FCFD-Laser-main/Manual_Scans/PulseWidthVsAmplitude_March25-1.svg')

plt.show()