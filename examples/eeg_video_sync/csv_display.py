import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt

# This flag, if true, will turn all unix timestamps to DATETIME (up to ms)
CONVERT_TO_DATETIME = True

# This flag, if true, will make the datetimes start from 01:00:00 instead of the time they were
# recorded. It makes the data easier to compare to the video.
PULL_TO_EPOCH = False

# Full path of the CSV file
PATH = r"C:\Users\enesy\Videos\Brain Battle\Synch App\Synchronization\eeg_video_sync\EEG_recording_2024-11-16-09.47.06.csv"
df = pd.read_csv(PATH)

if CONVERT_TO_DATETIME:
    initial_timestamp = df["timestamps"][0]
    df["timestamps"] = df["timestamps"].apply(lambda x: dt.datetime.fromtimestamp(x, tz=dt.timezone.utc))
    print(df["timestamps"][0])

fig, axs = plt.subplots(4, sharex=True, sharey=True, layout="constrained",  )
axs[0].plot(df["timestamps"], df["TP9"])
axs[0].set_title("TP9")
axs[1].plot(df["timestamps"], df["AF7"], "tab:orange")
axs[1].set_title("AF7")
axs[2].plot(df["timestamps"], df["TP10"], "tab:red")
axs[2].set_title("TP10")
axs[3].plot(df["timestamps"], df["AF8"], "tab:green")
axs[3].set_title("AF8")

if CONVERT_TO_DATETIME and PULL_TO_EPOCH:
    plt.gca().xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S.%f"))

plt.show()