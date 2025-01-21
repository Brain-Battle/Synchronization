import ffmpeg
import datetime as dt
import pandas as pd
from moviepy import VideoFileClip
import sys

# Paths to the video and CSV
video_path = r"E:\Fall Semester 2024\Videos\Round 2.MOV"
csv_path = r"E:\Fall Semester 2024\eeg data\EEG_recording_2024-11-16-09.47.06.csv"
output_path = r"E:\Fall Semester 2024\Videos\Adjusted_Video4.mp4"

try:
    # Extract video creation time
    video_metadata = ffmpeg.probe(video_path)
    creation_time = video_metadata["streams"][0]["tags"]["creation_time"]
    video_creation_dt = dt.datetime.strptime(creation_time, "%Y-%m-%dT%H:%M:%S.%f%z")
    video_creation_timestamp = video_creation_dt.timestamp()

    # Read the CSV
    df = pd.read_csv(csv_path)

    # Extract initial timestamp from the CSV
    initial_csv_timestamp = df["timestamps"][0]

    # Calculate the adjustment needed
    time_difference = initial_csv_timestamp - video_creation_timestamp
    print(f"Video creation timestamp: {video_creation_timestamp}")
    print(f"Initial CSV timestamp: {initial_csv_timestamp}")
    print(f"Time difference (seconds): {time_difference}")

    # Load the video
    with VideoFileClip(video_path) as video:
        video_duration = video.duration  # Get the total duration of the video
        print(f"Video duration: {video_duration} seconds")

        # Adjust start and end times
        if time_difference > 0:
            # Video starts later than CSV
            start_time = abs(time_difference)
            end_time = video_duration
        else:
            # Video starts earlier or at the same time as CSV
            start_time = 0
            end_time = video_duration - abs(time_difference)

        # Clamp start and end times to valid video ranges
        start_time = max(0, start_time)
        end_time = min(video_duration, max(0, end_time))

        print(f"Calculated start_time: {start_time}")
        print(f"Calculated end_time: {end_time}")

        # Check for valid subclip range
        if start_time >= end_time:
            print("The adjusted time range is invalid (no overlap with video duration).")
            sys.exit(1)

        # Create and save the adjusted subclip
        adjusted_video = video.subclipped(start_time, end_time)
        adjusted_video.write_videofile(output_path, codec="libx264")
        print(f"Adjusted video saved to: {output_path}")

except Exception as e:
    print(f"An error occurred: {e}")
