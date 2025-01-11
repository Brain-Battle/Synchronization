from moviepy.editor import clips_array, VideoFileClip, concatenate_videoclips

class VideoMerger:
    def __init__(self):
        self.slots = [[None, None],
                      [None, None]]

    def video_input(self, video, row, column):
        if not (0 <= row <= 1):
            raise ValueError("Slot index must be between 0 and 3.")
        self.slots[row][column] = VideoFileClip(video)

    def export(self, output_path, threads=1):
        final_clip = clips_array(self.slots)
        final_clip.resize(width=1920, height=1080).write_videofile(output_path, codec="libx264", audio_codec="aac", threads=threads)