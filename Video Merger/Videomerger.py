from moviepy.editor import VideoFileClip, concatenate_videoclips

class VideoMerger:
    def __init__(self):
        self.slots = [None] * 4

    def video_input(self, video, slot_index):
        if not (0 <= slot_index < 4):
            raise ValueError("Slot index must be between 0 and 3.")
        self.slots[slot_index] = video

    def export(self, output_path):
        videos = [VideoFileClip(path) for path in self.slots if path]
        if not videos:
            raise RuntimeError("No videos have been inputted.")
        final_clip = concatenate_videoclips(videos)
        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")


class UploadButton:
    @staticmethod
    def on_click(video, slot_index, merger):
        merger.video_input(video, slot_index)


class ExportButton:
    @staticmethod
    def on_click(output_path, merger):
        merger.export(output_path)
