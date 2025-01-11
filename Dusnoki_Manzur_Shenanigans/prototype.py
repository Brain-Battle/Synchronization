from typing import List

import pygame
from moviepy import VideoFileClip
import numpy as np
from scipy import signal
import os


# Function to get the file name from a path
def get_file_name(path):
    file_name = os.path.basename(path)
    file = os.path.splitext(file_name)
    return file[0]


# Function to initialize and update the Pygame progress bar
def show_progress_bar(video_path, total_frames, frame_callback):
    # Initialize Pygame
    pygame.init()

    # Set up Pygame window
    screen_width, screen_height = 500, 100
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption(f"Processing Audio of {get_file_name(video_path)}")

    # Colors
    background_color = (30, 30, 30)
    progress_bar_color = (0, 150, 255)
    text_color = (255, 255, 255)

    # Font
    font = pygame.font.Font("Fonts/Droid_Sans_Mono_Slashed_400.ttf", 24)

    # Progress bar variables
    progress_bar_width = screen_width - 40
    progress_bar_height = 20
    progress_x = 20
    progress_y = 50

    # Initialize frame count
    frame_count = 0
    running = True

    while running and frame_count < total_frames:
        # Event loop to handle quitting the window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                return

        # Process the next frame via callback
        frame_count = frame_callback(frame_count)

        # Calculate progress
        progress = frame_count / total_frames

        # Draw progress bar
        screen.fill(background_color)
        progress_text = font.render(f"Processing: {int(progress * 100)}%", True, text_color)
        screen.blit(progress_text, (20, 10))
        pygame.draw.rect(
            screen,
            progress_bar_color,
            (progress_x, progress_y, progress * progress_bar_width, progress_bar_height),
        )

        # Update display
        pygame.display.flip()

    pygame.quit()

# # Function to process the audio of a video
# def process_audio(video_path):
#     video = VideoFileClip(video_path)
#     audio_iter = video.audio.iter_frames()
#     total_frames = int(video.audio.fps * video.audio.duration)
#
#     audio_samples = []
#
#     def frame_callback(frame_count):
#         try:
#             frame = next(audio_iter)
#             audio_samples.append(frame)
#             return frame_count + 1
#         except StopIteration:
#             return total_frames
#
#     show_progress_bar(video_path, total_frames, frame_callback)
#
#     # Convert collected frames to numpy array and process stereo to mono
#     audio = np.array(audio_samples, dtype=np.float32).T
#     final_audio = (audio[0] + audio[1]) / 2.0
#
#     print(f"Audio processing complete for {get_file_name(video_path)}.")
#     return final_audio
#
#
# # Example Usage
# final_audio1 = process_audio("v1_path")
# final_audio2 = process_audio("v2_path")
#
# # Calculate correlation
# corr = signal.correlate(final_audio1, final_audio2, mode="same", method="fft")
#
# # Compute lags
# lags = signal.correlation_lags(len(final_audio1), len(final_audio2), mode="same")
#
# # Find maximum correlation
# max_corr = np.argmax(corr)
# print(f"Maximum correlation index: {max_corr}")
#
# # Convert lag to time delay in seconds
# time_delay = lags[max_corr] / 44100
# print(f"The amount of seconds the 2nd video is delayed is: {time_delay} sec")

"""
STEPS:

1. FIGURE OUT LONGEST VIDEO
2. FIGURE OUT ALL DELAYS COMPARED TO LONGEST VIDEO
3. SHIFT ALL VIDEOS ACCORDING TO DELAY (TO BE DONE) 
    i.e. if delay = 1s, shift 2nd video forward by 1s
    i.e. if delay = -1s, shift 2nd back by 1s
4. yay :D autosync done

def autosync():
    def find_longest_vid() -> int video_num
    def find_all_delays -> list[floats]
    def shift_all_videos -> None but it shifts using moviepy or whatever gpt cooks
"""

def find_longest_vid(video_paths) -> int:
    return_val = 0
    max_duration = -1
    for i, video_path in enumerate(video_paths):
        with VideoFileClip(video_path) as video:
            duration = video.duration
        if duration > max_duration:
            max_duration = duration
            return_val = i

    return return_val

def process_audio(video_path):
    video = VideoFileClip(video_path)
    audio_iter = video.audio.iter_frames()
    total_frames = int(video.audio.fps * video.audio.duration)

    audio_samples = []

    def frame_callback(frame_count):
        try:
            frame = next(audio_iter)
            audio_samples.append(frame)
            return frame_count + 1
        except StopIteration:
            return total_frames

    show_progress_bar(video_path, total_frames, frame_callback)

    # Convert collected frames to numpy array and process stereo to mono
    audio = np.array(audio_samples, dtype=np.float32).T
    final_audio = (audio[0] + audio[1]) / 2.0

    print(f"Audio processing complete for {get_file_name(video_path)}.")
    return final_audio

def find_all_delays(video_paths) -> List[float]:
    return_val = [0.0, 0.0, 0.0, 0.0] # Delays
    longest_index = find_longest_vid(video_paths)
    processed_audios = []
    for video_path in video_paths:
        processed_audios.append(process_audio(video_path))

    for i in range(4):
        if i != longest_index:
            corr = signal.correlate(processed_audios[longest_index],
                                    processed_audios[i],
                                    mode="same",
                                    method="fft")
            # Compute lags
            lags = signal.correlation_lags(len(processed_audios[longest_index]),
                                           len(processed_audios[i]),
                                           mode="same")
            # Find maximum correlation
            max_corr = np.argmax(corr)
            time_delay = lags[max_corr] / 44100

            return_val[i] = time_delay

    return return_val

delays = find_all_delays(["video_1_path", "video_2_path", "video_3_path", "video_4_path"])
for i in range(4):
    print(f"{delays[i]}s\n")