import ffmpeg
import datetime as dt
import pandas as pd

video_metadata = ffmpeg.probe(r"C:\Users\enesy\Videos\Brain Battle\eeg_video_sync\Round1.MOV")

creation_time = video_metadata["streams"][0]["tags"]["creation_time"]

date_time = dt.datetime.strptime(creation_time, "%Y-%m-%dT%H:%M:%S.%f%z")
print(date_time)
print(date_time.timestamp())

# Full path of the CSV file
PATH = r"C:\Users\enesy\Videos\Brain Battle\eeg_video_sync\EEG_recording_2024-11-16-09.47.06.csv"
df = pd.read_csv(PATH)

initial_timestamp = df["timestamps"][0]

difference_in_sec = date_time.timestamp() - df["timestamps"][0]

print(f"Difference: {difference_in_sec}")