import vlc
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
                             QGridLayout, QSlider, QCheckBox, QFileDialog, QDesktopWidget, QFrame)
from PyQt5.QtCore import Qt, QTimer
import sys


class VideoSyncApp(QWidget):
    """
    A GUI for syncing and playing back 4 videos simultaneously

    Attributes:
        width (int): Width of the window
        height (int): Height of the window
        media_players (list): List of media player instances for each video
        video_widgets (list): List of video display widgets
        timer (QTimer): Timer for updating the slider position
    """

    def __init__(self):
        """
        Initializes the main window and sets up UI components
        """

        super().__init__()

        # Window dimensions
        self.width = 1200
        self.height = 800

        # Initialize holders for video player instances and display widgets
        self.media_players = [None, None, None, None]
        self.video_widgets = [None, None, None, None]

        # Fix window size and disable maximize button
        self.setFixedSize(self.width, self.height)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)

        # Set up the UI
        self.initUI()

        # Set timer to update slider position every 10 ms
        self.timer = QTimer(self)
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update_slider_position)
        self.timer.start()

    def initUI(self):
        """
        Initializes the UI layout and its components
        """

        self.setWindowTitle('BattleUI')
        screen_geometry = QDesktopWidget().availableGeometry()

        # Center the window on the screen
        screen_center_x = (screen_geometry.width() - self.width) // 2
        screen_center_y = (screen_geometry.height() - self.height) // 2
        self.setGeometry(screen_center_x, screen_center_y, self.width, self.height)

        main_layout = QVBoxLayout()

        # Top layout for video panels and upload buttons
        top_layout = QHBoxLayout()

        # Left panel for video 1 and 3 upload buttons and data display
        left_panel = QVBoxLayout()
        self.video_data_1 = QLabel('Video Data\n00:00')
        self.filename_1 = QLabel('Filename')
        self.upload_btn_1 = QPushButton('Upload Video 1')
        self.upload_btn_1.clicked.connect(lambda: self.upload_video(1))

        self.video_data_3 = QLabel('Video Data\n00:00')
        self.filename_3 = QLabel('Filename')
        self.upload_btn_3 = QPushButton('Upload Video 3')
        self.upload_btn_3.clicked.connect(lambda: self.upload_video(3))

        left_panel.addWidget(self.video_data_1)
        left_panel.addWidget(self.filename_1)
        left_panel.addWidget(self.upload_btn_1)
        left_panel.addWidget(self.upload_btn_3)
        left_panel.addWidget(self.video_data_3)
        left_panel.addWidget(self.filename_3)

        # Right panel for video 2 and 4 upload buttons and data display
        right_panel = QVBoxLayout()
        self.video_data_2 = QLabel('Video Data\n00:00')
        self.filename_2 = QLabel('Filename')
        self.upload_btn_2 = QPushButton('Upload Video 2')
        self.upload_btn_2.clicked.connect(lambda: self.upload_video(2))

        self.video_data_4 = QLabel('Video Data\n00:00')
        self.filename_4 = QLabel('Filename')
        self.upload_btn_4 = QPushButton('Upload Video 4')
        self.upload_btn_4.clicked.connect(lambda: self.upload_video(4))

        right_panel.addWidget(self.video_data_2)
        right_panel.addWidget(self.filename_2)
        right_panel.addWidget(self.upload_btn_2)
        right_panel.addWidget(self.upload_btn_4)
        right_panel.addWidget(self.video_data_4)
        right_panel.addWidget(self.filename_4)

        # Center panel for displaying video frames in a grid layout
        central_panel = QGridLayout()
        self.video_display_1 = QFrame()
        self.video_display_1.setFixedSize(400, 300)
        self.video_display_1.setStyleSheet("border: 1px solid black;")

        self.video_display_2 = QFrame()
        self.video_display_2.setFixedSize(400, 300)
        self.video_display_2.setStyleSheet("border: 1px solid black;")

        self.video_display_3 = QFrame()
        self.video_display_3.setFixedSize(400, 300)
        self.video_display_3.setStyleSheet("border: 1px solid black;")

        self.video_display_4 = QFrame()
        self.video_display_4.setFixedSize(400, 300)
        self.video_display_4.setStyleSheet("border: 1px solid black;")

        # Populating video widgets list
        self.video_widgets = [self.video_display_1, self.video_display_2, self.video_display_3, self.video_display_4]

        central_panel.addWidget(self.video_display_1, 0, 0)
        central_panel.addWidget(self.video_display_2, 0, 1)
        central_panel.addWidget(self.video_display_3, 1, 0)
        central_panel.addWidget(self.video_display_4, 1, 1)

        top_layout.addLayout(left_panel)
        top_layout.addLayout(central_panel)
        top_layout.addLayout(right_panel)

        # Bottom panel for controls and data displays
        bottom_panel = QVBoxLayout()

        slider_panel = QHBoxLayout()

        # Slider for adjusting playback position
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setValue(0)
        self.time_slider.sliderReleased.connect(self.update_video_positions)
        slider_panel.addWidget(self.time_slider)

        # Checkbox for timecode display (functionality to be added)
        self.timecode_checkbox = QCheckBox('Timecode')
        slider_panel.addWidget(self.timecode_checkbox)

        # EEG upload button (functionality to be added)
        self.upload_eeg_btn = QPushButton('Upload EEG')
        slider_panel.addWidget(self.upload_eeg_btn)

        # Auto-sync button (functionality to be added)
        self.auto_sync_btn = QPushButton('Auto Sync')
        slider_panel.addWidget(self.auto_sync_btn)

        # Play/Pause button for controlling all videos
        self.play_pause_btn = QPushButton('Play/Pause')
        self.play_pause_btn.clicked.connect(self.play_pause_all_videos)
        slider_panel.addWidget(self.play_pause_btn)

        # Label for EEG data display
        self.eeg_data_display = QLabel('EEG Data Display')
        self.eeg_data_display.setFixedHeight(50)
        self.eeg_data_display.setStyleSheet("border: 1px solid black;")
        bottom_panel.addWidget(self.eeg_data_display)

        bottom_panel.addLayout(slider_panel)

        # Set main layout
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_panel)
        self.setLayout(main_layout)

    def upload_video(self, video_num):
        """
        Opens a file dialog to select a video file, initializes the VLC media player
        for the selected video, and displays it within its widget

        Args:
            video_num (int): The index of the video to be uploaded
        """

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Video File", "",
                                                   "Video Files (*.mp4 *.avi *.mov);;All Files (*)", options=options)

        if file_name:
            if not self.media_players[video_num - 1]:
                # Initialize VLC media player for the selected video widget
                self.media_players[video_num - 1] = vlc.MediaPlayer()
                # Set the window handle (HWND) for the media player so that the video displays within its widget
                self.media_players[video_num - 1].set_hwnd(int(self.video_widgets[video_num - 1].winId()))

            # Debugging statement
            print(f"Attempting to load video {video_num} from: {file_name}")
            media = vlc.Media(file_name)
            self.media_players[video_num - 1].set_media(media)

            # Update UI labels with the filename and video duration
            duration_ms = media.get_duration()
            duration_str = self.format_time(duration_ms // 1000)

            if video_num == 1:
                self.filename_1.setText(f'Filename\n{file_name}')
                self.video_data_1.setText(f'Video Data\n{duration_str}')
            elif video_num == 2:
                self.filename_2.setText(f'Filename\n{file_name}')
                self.video_data_2.setText(f'Video Data\n{duration_str}')
            elif video_num == 3:
                self.filename_3.setText(f'Filename\n{file_name}')
                self.video_data_3.setText(f'Video Data\n{duration_str}')
            elif video_num == 4:
                self.filename_4.setText(f'Filename\n{file_name}')
                self.video_data_4.setText(f'Video Data\n{duration_str}')

    def play_pause_all_videos(self):
        """
        Toggles play/pause state for all video players
        """

        for player in self.media_players:
            if player:
                if player.is_playing():
                    player.pause()
                else:
                    player.play()

    def update_video_positions(self):
        """
        Updates the playback position of each video based on the slider position
        """

        position_percentage = self.time_slider.value() / 100
        for player in self.media_players:
            if player and player.get_length() > 0:
                new_position = int(player.get_length() * position_percentage)
                player.set_time(new_position)

    def update_slider_position(self):
        """
        Updates the slider position to match the playback position of the first video
        """

        if self.media_players[0] and self.media_players[0].get_length() > 0:
            current_time = self.media_players[0].get_time()
            total_length = self.media_players[0].get_length()
            slider_value = int((current_time / total_length) * 100)
            self.time_slider.blockSignals(True)
            self.time_slider.setValue(slider_value)
            self.time_slider.blockSignals(False)

    def format_time(self, seconds):
        """
        Formats a time value in seconds into a mm:ss string format

        Args:
            seconds (int): Time in seconds

        Returns:
            str: Formatted time string as mm:ss
        """

        mins, secs = divmod(int(seconds), 60)
        return f"{mins:02}:{secs:02}"


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = VideoSyncApp()
    ex.show()
    sys.exit(app.exec_())

"""
TO-DO:
- Add functionality to EEG button, auto sync button, and timecode checkbox.
- Fix bug where the timeline cannot be used after the video ends.
- Make timeline smoother, if possible.
"""
