from moviepy import VideoFileClip, CompositeVideoClip, clips_array, vfx
from ..sync_utils.audio_analysis import find_all_delays

class VideoMerger:
    """
        A video merger interface that uses moviepy.
    """

    def __init__(self):
        """
            Have an array that contains 4 video slots
        """
        self.video_paths: list[str | None] =  [None, None, None, None]
        self.videos_array: list[VideoFileClip | None] = [None, None, None, None]
        self.current_composite: CompositeVideoClip | None = None

    def video_input(self, row: int, column: int, video_path: str, replace: bool = False):
        """
            Inputs an individual video

            Arguments:
            - row (int): Value from 0 to 1, it represents whether the video will be on top or bottom in the grid layout.
            - column (int): Value from 0 to 1, it represents whether the video will be on left or right in the grid layout.
            - video_path (str): Path to the video.
            - replace (bool) (default: False): If there is already a video, should we replace it? If False, function will not do anything.
            If True, existing video in that row and column will be replaced with this one.
        """
        # Check if row is valid
        if row > 1 or row < 0:
            print("Invalid row, must be either 0 or 1.")
            return

        # Check if column is valid
        if column > 1 or column < 0:
            print("Invalid row, must be either 0 or 1.")
            return
        
        # Internally, we keep the list flattened. Therefore we convert 
        # the index from binary (e.g [1][0]) to decimal (e.g [2])
        flattened_index = (row * 2) + column
        
        if self.video_paths[flattened_index] != None and replace == False:
            print(f"A video already exists at row {row} and column {column}. Set replace=True to replace it.")

        self.videos_array[row][column] = VideoFileClip(str)
        self.video_paths[row][column] = str

    def remove_video(self, row: int, column: int):
        """
            Remove a video. If a video does not exists at the given index, function will do nothing.

            Arguments:
            - row (int): Value from 0 to 1, it represents whether the video will be on top or bottom in the grid layout.
            - column (int): Value from 0 to 1, it represents whether the video will be on left or right in the grid layout.
        """
        # Check if row is valid
        if row > 1 or row < 0:
            print("Invalid row, must be either 0 or 1.")
            return

        # Check if column is valid
        if column > 1 or column < 0:
            print("Invalid row, must be either 0 or 1.")
            return
        
        flattened_index = (row * 2) + column
        
        self.videos_array[flattened_index] = None
        self.video_paths[flattened_index] = None

    def synchronize(self):
        """
            Synchronizes and places the video clips with each other.

            Saves the result at self.current_composite
        """

        delays = find_all_delays(self.video_paths)
        durations = [video.duration for video in self.videos_array]

        for index, video in enumerate(self.videos_array):
                # If the delay of the video is negative:
                if delays[index] < 0:
                    # We trim the video from the start
                    self.videos_array[index] = video.subclipped(delays[index], video.duration)
                    
                    # Update the corresponding video's duration
                    durations[index] -= round(delays[index])

                else: # If the delay is positive
                    # We delay/push the videos start by the amount
                    self.videos_array[index] = video.with_start(abs(delays[index]))

        self.current_composite = clips_array(self.videos_array)
        self.current_composite = self.current_composite.subclipped(max(delays), min(durations))
        self.current_composite = self.current_composite.resized(width=3840, height=2160)
    
    def preview(self):
        """
            Preview the merged video
        """
        try:
            self.current_composite.preview()
        except:
            print("Please upload all four videos and synchronize.")
            return
