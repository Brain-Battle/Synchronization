import ffmpeg
import datetime as dt
import pandas as pd

# Get video information, this will give a lot of JSON information
video_metadata = ffmpeg.probe(r"C:\Users\enesy\Videos\xd\2.MOV")

# Find creation time of the video
creation_time = video_metadata["streams"][0]["tags"]["creation_time"]

# In case the above line fails, print the whole metadata and you can figure out where the information is.
# print(video_metadata)

# Conver creation time to datetime object
date_time = dt.datetime.strptime(creation_time, "%Y-%m-%dT%H:%M:%S.%f%z")
print(date_time) # This is the datetime
print(date_time.timestamp()) # This is the datetime converted to timestamp

# Full path of the CSV file
PATH = r"C:\Users\enesy\Videos\Brain Battle\eeg_video_sync\EEG_recording_2024-11-16-09.47.06.csv"
df = pd.read_csv(PATH) # Read CSV with pandas

# Get the first timestamp of the EEG
initial_timestamp = df["timestamps"][0]

# Find the difference between two, this will be in terms of seconds
difference_in_sec = date_time.timestamp() - df["timestamps"][0]

# Print the result
print(f"Difference: {difference_in_sec}")