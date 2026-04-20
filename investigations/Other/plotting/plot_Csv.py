

import pandas as pd
import matplotlib.pyplot as plt
import os
import glob
from scipy.interpolate import interp1d

folder = r"C:/Users/zohra/Downloads/csv_files/download"

mean_files = sorted(glob.glob(os.path.join(folder, "mean_arrays_Z_*um.csv")))

plt.figure(figsize=(10,6))

first_mean_df = pd.read_csv(mean_files[0])
first_mean_df.columns = first_mean_df.columns.str.strip()
common_x = first_mean_df['X[um]']

for mean_csv in mean_files:
    z_label = os.path.basename(mean_csv).split("_Z_")[1].replace("um.csv", " µm")

    mean_df = pd.read_csv(mean_csv)
    mean_df.columns = mean_df.columns.str.strip()

    f = interp1d(mean_df['X[um]'], mean_df['CH3'], kind='linear', fill_value="extrapolate")
    y = f(common_x)


    plt.scatter(common_x, y, s=25, alpha=0.7, edgecolors='none', label=f"CH3 at Z = {z_label}")


plt.xlabel("X [µm]", fontsize=12)
plt.ylabel(" [mV]", fontsize=12)
plt.title("CH3  vs X at Different Heights", fontsize=14)

plt.legend(title="Heights", loc='upper right', fontsize=9, title_fontsize=10, frameon=True)

plt.grid(True, linestyle="--", alpha=0.7)


output_file = os.path.join(folder, "CH3_vs_x_different_heights.png")
plt.savefig(output_file, dpi=300)

plt.show()

