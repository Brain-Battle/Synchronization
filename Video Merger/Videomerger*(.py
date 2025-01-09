from moviepy.editor import *
import os

# Paths of the video files
video_1_path = 'movie1.mp4'
video_2_path = 'movie2.mp4'

if not os.path.exists(video_1_path):
    raise FileNotFoundError(f"The file '{video_1_path}' does not exist.")
if not os.path.exists(video_2_path):
    raise FileNotFoundError(f"The file '{video_2_path}' does not exist.")

# Load the clips here 
clip_01 = VideoFileClip(video_1_path)
clip_02 = VideoFileClip(video_2_path)

# Standardize resolution 
height = min(clip_01.h, clip_02.h) 
clip_01 = clip_01.resize(height=height)
clip_02 = clip_02.resize(height=height)

# Concatenating clips
try:
    result_clip = concatenate_videoclips([clip_01, clip_02])
except Exception as e:
    print(f"Error during concatenation: {e}")
    raise

# output file
output_path = 'combined.mp4'
try:
    result_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
except Exception as e:
    print(f"Error writing the video file: {e}")
    raise

print(f"Video successfully saved as '{output_path}'")