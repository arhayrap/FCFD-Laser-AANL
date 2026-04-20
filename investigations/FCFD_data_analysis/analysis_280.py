import ROOT
import uproot as ur
import numpy as np
import matplotlib.pyplot as plt


BASE_PATH = "/home/arcadia/Documents/Motors_automation_test/DAQtest/280runs/280_runs_converted/"
FIGURES_PATH = "/home/arcadia/Documents/Motors_automation_test/DAQtest/280runs/figures/"        # # folder to save the plots

data_path_array = []

# # adding the files to the array of paths
# for file in os.listdir(BASE_PATH):
#     if file.endswith(".root"):
#         data_path_array.append(BASE_PATH + file)


# first scan by X with constant Z
# every 70 runs the Z coordinate changes by 250 um

# initial_run_number = 1
# initial_run_number = 71
# initial_run_number = 141
initial_run_number = 211  



if initial_run_number == 1: 
    Z_coordinate = 85000
elif initial_run_number == 71:
    Z_coordinate = 85250
elif initial_run_number == 141:
    Z_coordinate = 85500
elif initial_run_number == 211:
    Z_coordinate = 85750

for i in range (initial_run_number, initial_run_number + 70):
    data_path_array.append(BASE_PATH + f"converted_run{i}.root")

# print(len(data_path_array))

'''
root file number -> Z coordinate
1-71    ----------> 85000 um
71-141  ----------> 85250 um
141-211 ----------> 85500 um
211-281 ----------> 85750 um
'''



# iChannel = 1
# iChannel = 3
iChannel = 5 #to do after lunch
'''
iChannel -> Scope Channel
0 --------> CH1 (Trigger Channel)
1 --------> CH2 (Analog 1)
2 --------> CH3 (Discriminator 1)
3 --------> CH4 (Analog 2)
4 --------> CH5 (Discriminator 2)
5 --------> CH6 (Analog 3)
6 --------> CH7 (Discriminator 3)
'''
x_array = []
initial_x = 45750 # to 46095 by 5
current_x = initial_x
step_x = 5

# ch1_mean_array = []

mean_of_means_array = []

current_index = 1
for data_path in data_path_array:

    data = ur.open(data_path)["pulse"]
    out_data = data.arrays(["time", "channel"], library="np")

    SignalMeanOfEvent = []

    for iEvent in range(0, 1000):
        first_index = np.where(out_data["channel"][iEvent, iChannel, :] > 0.1)[0][0]
        last_index = np.where(out_data["channel"][iEvent, iChannel, :] > 0.1)[0][-1]
        SignalMeanOfEvent.append(np.mean(out_data["channel"][iEvent, iChannel, first_index + 10 : last_index - 10]))

    mean_value = sum(SignalMeanOfEvent) / len(SignalMeanOfEvent)
    print(f"{current_index}\t: {mean_value:.7f} V.")

    mean_of_means_array.append(mean_value)

    current_index += 1

    x_array.append(current_x)
    current_x += step_x

# saving as csv
combined_array = np.column_stack((x_array, mean_of_means_array))
np.savetxt('arrays.csv', combined_array, delimiter=',', header='x_array,mean_of_means_array', comments='', fmt='%f')

# plotting
plt.plot(x_array, mean_of_means_array, color="blue")
plt.title(f"Signal Mean vs X position (Scope Channel {iChannel + 1}). Z = {Z_coordinate} um")
plt.xlabel("X coordinate [um]")
plt.ylabel("Signal mean [V]")
plt.grid(True)


# # saving as an image
plt.savefig(f'{FIGURES_PATH}Channel{iChannel}_Z{Z_coordinate}.pdf')
plt.savefig(f'{FIGURES_PATH}Channel{iChannel}_Z{Z_coordinate}.eps')
plt.savefig(f'{FIGURES_PATH}Channel{iChannel}_Z{Z_coordinate}.svg')
# plt.savefig(f'{FIGURES_PATH}Channel{iChannel}.jpg')




# # showing the plot
plt.show()