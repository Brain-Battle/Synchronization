class VideoMerger:
    """
        A video merger interface that uses moviepy or ffmpeg.
    """

    def __init__(self):
        """
            Have an array that contains 4 video slots
        """
        pass

    def video_input():
        """
            Inputs an individual video
        """
        pass

    def export():
        """
            Exports merged video
        """
        pass


class UploadButton:
    def on_click():
        video = ""
        VideoMerger.video_input(video)

class ExportButton:
    def on_click():
        video_path_to_save = ""
        VideoMerger.export(video_path_to_save)

