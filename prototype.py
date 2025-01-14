from typing import List
from moviepy import VideoFileClip
import numpy as np
from scipy import signal
import os


# Function to get the file name from a path
def get_file_name(path):
    file_name = os.path.basename(path)
    file = os.path.splitext(file_name)
    return file[0]


def process_audio(video_path, comparison_index):
    video = VideoFileClip(video_path)
    audio = video.audio.to_soundarray().T

    final_audio = (audio[0] + audio[1]) / 2.0
    print(f"Audio processing complete for {get_file_name(video_path)} compared to video #{comparison_index}.")
    return final_audio


def find_all_delays(video_paths: List[str], comparison_index=0) -> List[float]:
    delays = [0.0] * len(video_paths)
    processed_audios = [process_audio(path, comparison_index) for path in video_paths]

    for i in range(len(video_paths)):
        if i != comparison_index:
            corr = signal.correlate(processed_audios[comparison_index],
                                    processed_audios[i],
                                    mode="same",
                                    method="fft")

            lags = signal.correlation_lags(len(processed_audios[comparison_index]),
                                           len(processed_audios[i]),
                                           mode="same")

            max_corr = np.argmax(corr)
            time_delay = lags[max_corr] / 44100  # Convert to seconds
            print(time_delay)
            if time_delay < 0.0:
                return find_all_delays(video_paths, comparison_index=(comparison_index + 1))
            delays[i] = time_delay

    return delays
