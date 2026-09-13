from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA = Path(__file__).parent.parent / "data"
SOURCE = Path(__file__).with_name("step11.cpp")
IMGPATH = Path(__file__).parent.parent / "img"
REYNOLDS = 1000

def rmse(predictions, truth):
    return np.sqrt(((predictions - truth) ** 2).mean())

# Load velocity data
cfd_u_df = pd.read_csv(DATA / f"u_Re_{REYNOLDS}.csv")
cfd_v_df = pd.read_csv(DATA / f"v_Re_{REYNOLDS}.csv")
expt_u_df = pd.read_csv(DATA/ "ghiaData" / "verticalLine.csv")
expt_v_df = pd.read_csv(DATA/ "ghiaData" / "horizontalLine.csv")

# Normalize x and y coordinates and velocity values
cfd_u_df['xCoord'] = cfd_u_df['xCoord'] / cfd_u_df['xCoord'].max()
cfd_u_df['yCoord'] = cfd_u_df['yCoord'] / cfd_u_df['yCoord'].max()
cfd_u_df['value'] = cfd_u_df['value'] / cfd_u_df['value'].max()

cfd_v_df['xCoord'] = cfd_v_df['xCoord'] / cfd_v_df['xCoord'].max()
cfd_v_df['yCoord'] = cfd_v_df['yCoord'] / cfd_v_df['yCoord'].max()
cfd_v_df['value'] = cfd_v_df['value'] / cfd_v_df['value'].max()

# Extract subset where x = 0.5 and y = 0.5
cfd_u_x_05 = cfd_u_df[cfd_u_df['xCoord'] == 0.5]
cfd_v_y_05 = cfd_v_df[cfd_v_df['yCoord'] == 0.5]

# Interpolate CFD velocity data
cfd_u_x_05_interpolated = np.interp(expt_u_df['y'], cfd_u_x_05['yCoord'], cfd_u_x_05['value'])
cfd_v_y_05_interpolated = np.interp(expt_v_df['x'], cfd_v_y_05['xCoord'], cfd_v_y_05['value'])

# Calculate and return RMSE
u_rmse = rmse(predictions=cfd_u_x_05_interpolated, truth=expt_u_df[f'Re_{REYNOLDS}'])
v_rmse = rmse(predictions=cfd_v_y_05_interpolated, truth=expt_v_df[f'Re_{REYNOLDS}'])

print(f"Normalized u RMSE = {u_rmse:.04f} m/s")
print(f"Normalized v RMSE = {v_rmse:.04f} m/s")
print(f"Sum of Normalized u and v RMSE = {u_rmse + v_rmse:.04f} m/s")

# Plot and save velocity data
fig,ax = plt.subplots(2, figsize=(8,8))
fig.suptitle(f'Velocity data comparisons at Re = {REYNOLDS}, at x = 0.5 (top) and y = 0.5 (bottom) ')

ax[0].plot(cfd_u_x_05['value'], cfd_u_x_05['yCoord'], label='CFD', linestyle='-', marker='o')
ax[0].plot(expt_u_df[f'Re_{REYNOLDS}'], expt_u_df['y'], label="Ghia et al.", color='black', linestyle='-', marker='o')
ax[0].set_xlabel("U velocity (m/s)")
ax[0].set_ylabel("Y coordinate")
ax[0].legend(loc="lower right")
ax[0].set_aspect(1.0)

ax[1].plot(cfd_v_y_05['value'], cfd_v_y_05['xCoord'], label='CFD', linestyle='-', marker='o')
ax[1].plot(expt_v_df[f'Re_{REYNOLDS}'], expt_v_df['x'], label="Ghia et al.", color='black', linestyle='-', marker='o')
ax[1].set_xlabel("V velocity (m/s)")
ax[1].set_ylabel("X coordinate")
ax[1].legend(loc="upper right")
ax[1].set_aspect(1.0)

plt.tight_layout()
plt.savefig(IMGPATH / f"velocity_comparison_Re_{REYNOLDS}.png")
plt.show()