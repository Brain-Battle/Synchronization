import numpy as np
import moviepy.editor as editor
from scipy import signal

class Analyzer:
    """
        Extracts audio from a given video file clip, using moviepy and numpy.

        Arguments:
        - clip (VideoClip): A video clip imported with moviepy. Can also be a VideoFileClip.
        
        Returns:
        - NDArray that contains mono audio data. Data is reduced from two channel audio.
    """
    @staticmethod
    def extract_audio(clip: editor.VideoClip) -> np.ndarray:
        # Extract audio as a numpy array from the video.
        audio_samples = list(clip.audio.iter_frames())
        audio = np.array(audio_samples).T

        # Reduce two-channel stereo audio into single-channel mono
        # By adding two channels together and dividing by 2. 
        final_audio = (audio[0] + audio[1]) / 2.0

        return final_audio


    """
        Extracts audio from a given file, using moviepy and numpy.

        Arguments:
        - file_path (str): The file path to the video.
        
        Returns:
        - NDArray that contains mono audio data. Data is reduced from two channel audio.
    """
    @staticmethod
    def extract_audio_from_file(file_path: str) -> np.ndarray:
        # Load video1
        video1 = editor.VideoFileClip(file_path)

        # Extract audio as a numpy array from the video.
        audio_samples = list(video1.audio.iter_frames())
        audio = np.array(audio_samples).T

        # Reduce two-channel stereo audio into single-channel mono
        # By adding two channels together and dividing by 2. 
        final_audio = (audio[0] + audio[1]) / 2.0

        return final_audio

    """
        Calculates the time delay that second audio data has compared to the first one.
        A positive result means that the first audio is ahead of the second one.
        Therefore the second audio should be moved forward. (in a timeline)

        A negative result means that the first audio is behind the second one.
        Therefore either the first audio should be moved forward by the absolute value of the result,
        or the second video should be pulled back.

        The delay is calculated by applying cross_correlation to two audio data arrays.
        The result might not be 100% correct.

        Arguments:
        - audio_data1 (numpy.ndarray): Data 1
        - audio_data2 (numpy.ndarray): Data 2

        Returns:
        - lags (array): the amount of lag for each correlation
        - corr (array): correlation data between audios

    """
    @staticmethod
    def calculate_time_delay(audio_data1: np.ndarray, audio_data2: np.ndarray, sample_rate = 44100):
        # The method paramater does not matter much here.
        # fft is faster than the default.
        corr = signal.correlate(audio_data1, audio_data2, mode="same", method="fft")

        # correlation_lags method creates an array
        # that contains the possible delays according to each correlation
        # Its kind of like dark magic ngl.
        lags = signal.correlation_lags(len(audio_data1), len(audio_data2), mode="same")

        # The maximum correlation happens at the amount the second video is delayed compared to the first.
        max_corr = np.argmax(corr)

        # We divide the lag by the samples per second (44100 for a normal WAV file)
        # to find the amount "the second video" is delayed compared to the first.
        # Essentially convert the number from samples into seconds.
        time_delay = lags[max_corr] / sample_rate

        return time_delay
