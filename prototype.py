from typing import List
import pygame
from moviepy import VideoFileClip
import numpy as np
from scipy import signal
import os

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
    audio = video.audio.to_soundarray().T
    total_frames = int(video.audio.fps * video.audio.duration)

    audio_samples = []

    def frame_callback(frame_count):
        try:
            frame = next(audio)
            audio_samples.append(frame)
            return frame_count + 1
        except StopIteration:
            return total_frames
        
    show_progress_bar(video_path, total_frames, frame_callback)

    # Convert collected frames to numpy array and process stereo to mono
    final_audio = (audio[0] + audio[1]) / 2.0
    print(f"Audio processing complete for {get_file_name(video_path)}.")
    return final_audio

def find_all_delays(video_paths: List[str]) -> List[float]:
    if len(video_paths) < 2:
        raise ValueError("At least two video paths are required for autosync.")

    delays = [0.0] * len(video_paths)
    longest_index = find_longest_vid(video_paths)
    processed_audios = [process_audio(path) for path in video_paths]

    for i in range(len(video_paths)):
        if i != longest_index:
            corr = signal.correlate(processed_audios[longest_index], 
                                    processed_audios[i], 
                                    mode="same", 
                                    method="fft")
            
            lags = signal.correlation_lags(len(processed_audios[longest_index]), 
                                           len(processed_audios[i]), 
                                           mode="same")
            
            max_corr = np.argmax(corr)
            time_delay = lags[max_corr] / 44100  # Convert to seconds
            delays[i] = time_delay

    return delays

def autosync(video_paths: List[str]) -> List[float]:
    """Main function to calculate and return delays for autosync."""
    
    if not all(os.path.exists(path) for path in video_paths):
        raise FileNotFoundError("One or more video paths are invalid.")
    delays = find_all_delays(video_paths)
    return delays