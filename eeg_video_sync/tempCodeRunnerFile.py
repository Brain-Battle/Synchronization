# Load the video
# with VideoFileClip(video_path) as video:
#     # Shift the video timestamps by the time difference
#     start_time = max(0, -time_difference)  # Adjust start if difference is negative
#     end_time = video.duration + time_difference  # Adjust end based on difference

#     # Clamp start and end times to valid ranges
#     start_time = max(0, start_time)
#     end_time = min(video.duration, max(0, end_time))  # Ensure end_time is non-negative

#     if start_time >= video.duration or end_time <= 0:
#         print("The adjusted time range is outside the video duration. No valid subclip can be created.")
#     else:
#         print(f"Adjusted video range: start={start_time}, end={end_time}")

#         # Create the adjusted subclip
#         adjusted_video = video.subclip(start_time, end_time)

#         # Save the adjusted video
#         adjusted_video.write_videofile(output_path, codec="libx264")
#         print(f"Adjusted video saved to: {output_path}")
