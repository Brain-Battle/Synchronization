from moviepy import VideoFileClip, clips_array, vfx

class VideoMerger:
    """
        A video merger interface that uses moviepy or ffmpeg.
    """

    def __init__(self):
        """
            Have an array that contains 4 video slots
        """
        self.videos_array = [[None, None], 
                             [None, None]]
        pass

    def video_input(self, row: int, column: int, video: VideoFileClip):
        """
            Inputs an individual video
        """
        self.videos_array[row][column] = video

    def export(self):
        """
            Exports merged video
        """
        try:
            final_clip = clips_array(self.videos_array)
            final_clip = final_clip.resized(width=3840, height=2160)
            final_clip.write_videofile()
        except:
            print("Please upload all four videos.")
            return
