import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from datetime import datetime

# Flags for timestamp conversion
CONVERT_TO_DATETIME = False
PULL_TO_EPOCH = False

# Full path of the CSV file
PATH = r"C:\Users\enesy\Videos\Brain Battle\eeg_video_sync\EEG_recording_2024-11-16-09.47.06.csv"
df = pd.read_csv(PATH)

# Convert timestamps if the flag is set
if CONVERT_TO_DATETIME:
    initial_timestamp = df["timestamps"][0]
    df["timestamps"] = df["timestamps"].apply(lambda x: datetime.fromtimestamp(x - initial_timestamp))
    print(df["timestamps"][0])
else:
    df["timestamps"] = df["timestamps"].astype(float)  # Ensure timestamps are numeric

# Create the plot
fig, axs = plt.subplots(4, sharex=True, sharey=True, figsize=(10, 8), layout="constrained")

# Plot the data
lines = []
lines.append(axs[0].plot(df["timestamps"], df["TP9"], label="TP9")[0])
axs[0].set_title("TP9")
lines.append(axs[1].plot(df["timestamps"], df["AF7"], "tab:orange", label="AF7")[0])
axs[1].set_title("AF7")
lines.append(axs[2].plot(df["timestamps"], df["TP10"], "tab:red", label="TP10")[0])
axs[2].set_title("TP10")
lines.append(axs[3].plot(df["timestamps"], df["AF8"], "tab:green", label="AF8")[0])
axs[3].set_title("AF8")

# Add vertical line indicator
vlines = [ax.axvline(df["timestamps"][0], color="black", linestyle="--", label="Indicator") for ax in axs]

# Set x-axis format for datetime
if CONVERT_TO_DATETIME and PULL_TO_EPOCH:
    plt.gca().xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S.%f"))

# Slider for interaction
ax_slider = plt.axes([0.2, 0.01, 0.65, 0.03], facecolor="lightgoldenrodyellow")
slider = Slider(ax_slider, "Time Index", 0, len(df["timestamps"]) - 1, valinit=0, valstep=1)

# Update function for slider
def update(val):
    index = int(slider.val)
    timestamp = df["timestamps"][index]
    for vline in vlines:
        vline.set_xdata([timestamp, timestamp])  # Use a sequence
    fig.canvas.draw_idle()

# Connect slider to update function
slider.on_changed(update)

plt.show()
