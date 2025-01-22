import vlc
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QSlider, QCheckBox, QFileDialog, QDesktopWidget, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
import sys
import ffmpeg
import os
import subprocess

from prototype import autosync
from newLayout import HighlightSlider

from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl

class AspectRatioFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())  # Add a layout to manage children
        self.layout().setContentsMargins(0, 0, 0, 0)  # Remove margins

    def resizeEvent(self, event):
        # Get the new width and calculate height based on 16:9 aspect ratio
        width = self.width()
        height = int(width * 9 / 16)

        # Set the fixed size for the QFrame
        self.setFixedHeight(height)
        super().resizeEvent(event)

class VideoSyncApp(QWidget):
    def __init__(self):
        super().__init__()
        self.width = 1200
        self.height = 800
        self.media_players = [None, None, None, None]
        self.video_widgets = [None, None, None, None]
        self.video_paths = [None, None, None, None]
        self.eeg_paths = [None, None]
        self.initUI()
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.start()

    def initUI(self):
        self.setWindowTitle('BattleUI')
        self.setStyleSheet("background-color: #F3F3F1;")
        screen_geometry = QDesktopWidget().availableGeometry()
        screen_center_x = (screen_geometry.width() - self.width) // 2
        screen_center_y = (screen_geometry.height() - self.height) // 2
        self.setGeometry(screen_center_x, screen_center_y, self.width, self.height)

        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()

        # Left panel with buttons for Video 1 (top) and Video 3 (bottom)
        left_panel = QVBoxLayout()

        # Video 1: Top video, Edit button above Upload button
        self.edit_btn_1 = QPushButton('Edit Video 1')
        self.edit_btn_1.setStyleSheet("background-color: #FFFFFF;")
        self.edit_btn_1.clicked.connect(lambda: self.edit_video(1))
        self.edit_btn_1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.video_data_1 = QLabel('Video Data\n00:00')
        self.filename_1 = QLabel('Filename')

        self.upload_btn_1 = QPushButton('Upload Video 1')
        self.upload_btn_1.setStyleSheet("background-color: #FFFFFF;")
        self.upload_btn_1.clicked.connect(lambda: self.upload_video(1))
        self.upload_btn_1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        left_panel.addWidget(self.video_data_1)
        left_panel.addWidget(self.filename_1)
        left_panel.addWidget(self.edit_btn_1)
        left_panel.addWidget(self.upload_btn_1)

        # Video 3: Bottom video, Edit button below Upload button
        self.video_data_3 = QLabel('Video Data\n00:00')
        self.filename_3 = QLabel('Filename')

        self.upload_btn_3 = QPushButton('Upload Video 3')
        self.upload_btn_3.setStyleSheet("background-color: #FFFFFF;")
        self.upload_btn_3.clicked.connect(lambda: self.upload_video(3))
        self.upload_btn_3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.edit_btn_3 = QPushButton('Edit Video 3')
        self.edit_btn_3.setStyleSheet("background-color: #FFFFFF;")
        self.edit_btn_3.clicked.connect(lambda: self.edit_video(3))
        self.edit_btn_3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        left_panel.addWidget(self.upload_btn_3)
        left_panel.addWidget(self.edit_btn_3)
        left_panel.addWidget(self.video_data_3)
        left_panel.addWidget(self.filename_3)

        # Right panel with buttons for Video 2 (top) and Video 4 (bottom)
        right_panel = QVBoxLayout()

        # Video 2: Top video, Edit button above Upload button
        self.edit_btn_2 = QPushButton('Edit Video 2')
        self.edit_btn_2.setStyleSheet("background-color: #FFFFFF;")
        self.edit_btn_2.clicked.connect(lambda: self.edit_video(2))
        self.edit_btn_2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.video_data_2 = QLabel('Video Data\n00:00')
        self.filename_2 = QLabel('Filename')

        self.upload_btn_2 = QPushButton('Upload Video 2')
        self.upload_btn_2.setStyleSheet("background-color: #FFFFFF;")
        self.upload_btn_2.clicked.connect(lambda: self.upload_video(2))
        self.upload_btn_2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        right_panel.addWidget(self.video_data_2)
        right_panel.addWidget(self.filename_2)
        right_panel.addWidget(self.edit_btn_2)
        right_panel.addWidget(self.upload_btn_2)

        # Video 4: Bottom video, Edit button below Upload button
        self.video_data_4 = QLabel('Video Data\n00:00')
        self.filename_4 = QLabel('Filename')

        self.upload_btn_4 = QPushButton('Upload Video 4')
        self.upload_btn_4.setStyleSheet("background-color: #FFFFFF;")
        self.upload_btn_4.clicked.connect(lambda: self.upload_video(4))
        self.upload_btn_4.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.edit_btn_4 = QPushButton('Edit Video 4')
        self.edit_btn_4.setStyleSheet("background-color: #FFFFFF;")
        self.edit_btn_4.clicked.connect(lambda: self.edit_video(4))
        self.edit_btn_4.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        right_panel.addWidget(self.upload_btn_4)
        right_panel.addWidget(self.edit_btn_4)
        right_panel.addWidget(self.video_data_4)
        right_panel.addWidget(self.filename_4)

        # Central panel for video displays
        central_panel = QGridLayout()
        central_panel.setSpacing(0)  # Remove gaps between videos
        central_panel.setContentsMargins(0, 0, 0, 0)  # Remove margins around the grid

        self.video_display_1 = AspectRatioFrame(self)
        self.video_display_1.resize(400, 225)
        self.video_display_1.setStyleSheet("border: 1px solid black; box-sizing: border-box;")
        self.video_display_1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_display_1.setLayout(QVBoxLayout())  # Assign a layout

        self.video_display_2 = AspectRatioFrame(self)
        self.video_display_2.resize(400, 225)
        self.video_display_2.setStyleSheet("border: 1px solid black; box-sizing: border-box;")
        self.video_display_2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_display_2.setLayout(QVBoxLayout())  # Assign a layout

        self.video_display_3 = AspectRatioFrame(self)
        self.video_display_3.resize(400, 225)
        self.video_display_3.setStyleSheet("border: 1px solid black; box-sizing: border-box;")
        self.video_display_3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_display_3.setLayout(QVBoxLayout())  # Assign a layout

        self.video_display_4 = AspectRatioFrame(self)
        self.video_display_4.resize(400, 225)
        self.video_display_4.setStyleSheet("border: 1px solid black; box-sizing: border-box;")
        self.video_display_4.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_display_4.setLayout(QVBoxLayout())  # Assign a layout

        self.video_widgets = [self.video_display_1, self.video_display_2, self.video_display_3, self.video_display_4]

        self.eeg_data_display_1 = QLabel('EEG Data Display 1')
        self.eeg_data_display_1.setMaximumSize(672, 100)
        self.eeg_data_display_1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.eeg_data_display_1.setStyleSheet("border: 1px solid black;")

        self.eeg_data_display_2 = QLabel('EEG Data Display 2')
        self.eeg_data_display_2.setMaximumSize(672, 100)
        self.eeg_data_display_2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.eeg_data_display_2.setStyleSheet("border: 1px solid black;")

        self.time_slider = HighlightSlider(Qt.Horizontal)
        self.time_slider.setRange(0, 0)  # Set initial range
        self.time_slider.setValue(0)
        self.time_slider.sliderMoved.connect(self.set_position)  # Connect movement to video position

        central_panel.addWidget(self.video_display_1, 0, 0)
        central_panel.addWidget(self.video_display_2, 0, 1)
        central_panel.addWidget(self.video_display_3, 1, 0)
        central_panel.addWidget(self.video_display_4, 1, 1)
        central_panel.addWidget(self.eeg_data_display_1, 2, 0)
        central_panel.addWidget(self.eeg_data_display_2, 2, 1)
        central_panel.addWidget(self.time_slider, 4, 0, 1, 2)
        # Add stretch factors to layouts
        top_layout.addLayout(left_panel, 1)  # Fixed size
        top_layout.addLayout(central_panel, 5)  # Videos grow
        top_layout.addLayout(right_panel, 1)  # Fixed size

        bottom_panel = QVBoxLayout()
        slider_panel = QHBoxLayout()
        slider_panel_2 = QHBoxLayout()

        self.timecode_checkbox = QCheckBox('Timecode')
        slider_panel_2.addWidget(self.timecode_checkbox)

        self.upload_eeg_btn_1 = QPushButton('Upload EEG 1')
        self.upload_eeg_btn_1.setStyleSheet("background-color: #FFFFFF;")

        self.upload_eeg_btn_2 = QPushButton('Upload EEG 2')
        self.upload_eeg_btn_2.setStyleSheet("background-color: #FFFFFF;")

        self.auto_sync_btn = QPushButton('Auto Sync')
        self.auto_sync_btn.setStyleSheet("background-color: #FFFFFF;")
        self.auto_sync_btn.clicked.connect(self.auto_sync_videos)

        slider_panel_2.addWidget(self.upload_eeg_btn_1)
        slider_panel_2.addWidget(self.upload_eeg_btn_2)
        slider_panel_2.addWidget(self.auto_sync_btn)

        self.play_pause_btn = QPushButton('Play/Pause')
        self.play_pause_btn.setStyleSheet("background-color: #FFFFFF;")
        self.play_pause_btn.clicked.connect(self.play_pause_all_videos)
        slider_panel_2.addWidget(self.play_pause_btn)

        self.export_btn = QPushButton('Export')
        self.export_btn.setStyleSheet("background-color: #FFFFFF;")
        self.export_btn.clicked.connect(self.merge_videos)
        slider_panel_2.addWidget(self.export_btn)

        bottom_panel.addLayout(slider_panel)
        bottom_panel.addLayout(slider_panel_2)

        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_panel)

        self.setLayout(main_layout)

    def auto_sync_videos(self):
        # Collect video paths (ensure all videos are uploaded)
        video_paths = [path for path in self.video_paths if path]

        if len(video_paths) < 2:
            print("Please upload at least two videos before syncing.")
            return

        try:
            # Call the autosync function to calculate delays
            delays = autosync(video_paths)

            # Find the longest video's delay (it will serve as the reference)
            reference_delay = min(delays)

            # Adjust the playback positions of all videos relative to the reference
            for i, delay in enumerate(delays):
                if self.media_players[i]:  # Ensure the VLC media player exists
                    # Calculate the relative delay (positive or negative)
                    relative_delay = delay - reference_delay

                    # Adjust the starting position (in milliseconds)
                    start_position_ms = max(0, int(relative_delay * 1000))  # VLC expects milliseconds
                    self.media_players[i].set_time(start_position_ms)

            print("Videos have been synced successfully.")

        except Exception as e:
            print(f"Error during autosync: {e}")

    def upload_video(self, video_num):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Video File", "",
                                                "Video Files (*.mp4 *.avi *.mov);;All Files (*)", options=options)
        if file_name:
            self.video_paths[video_num - 1] = file_name
            if not self.media_players[video_num - 1]:
                self.media_players[video_num - 1] = QMediaPlayer()
                video_widget = QVideoWidget(self)
                self.media_players[video_num - 1].setVideoOutput(video_widget)
                self.video_widgets[video_num - 1].layout().addWidget(video_widget)

            media = QMediaContent(QUrl.fromLocalFile(file_name))
            self.media_players[video_num - 1].setMedia(media)

            self.media_players[video_num - 1].positionChanged.connect(self.position_changed)
            self.media_players[video_num - 1].durationChanged.connect(self.duration_changed)

            filename_label = getattr(self, f"filename_{video_num}")
            filename_label.setText(f"Filename:\n{file_name}")
            filename_label.setWordWrap(True)

    def edit_video(self, video_num):
        if not self.media_players[video_num - 1]:
            print("Error. No media loaded")
            return
        video_path = self.video_paths[video_num - 1]
        if not video_path:
            return
        print("Error. No video file path found")

        paths = " ".join([path if path else "skip" for path in self.video_paths])
        eeg_paths = " ".join([path if path else "skip" for path in self.eeg_paths])
        command = f"python newLayout.py {paths} {eeg_paths} {video_num}"
        print(command)

        # Saving resources
        print("Stopping Video_Page.py...")
        self.close()
        app.quit()

        # Launch the video editing page
        subprocess.run(command, shell=True)

        # Restart after editing as code freezes on subprocess.run
        print("Restarting Video_Page.py...")
        new_command = f"python Video_Page.py {paths} {eeg_paths}"
        subprocess.run(new_command, shell=True)

    def merge_videos(self):
        # Collect file paths for all videos
        file_paths = []
        for i in range(1, 5):  # Loop for videos 1 to 4
            filename_label = getattr(self, f"filename_{i}")
            file_path = filename_label.text().replace("Filename:\n", "").strip()
            if file_path:
                file_paths.append(file_path)
            else:
                print(f"Video {i} has not been loaded.")
                return

        # Check if all four videos are loaded
        if len(file_paths) != 4:
            print("Please load all four videos before exporting.")
            return

        # Output file name
        output_file = QFileDialog.getSaveFileName(
            self, "Save Merged Video", "", "Video Files (*.mp4 *.avi *.mov);;All Files (*)"
        )[0]
        if not output_file:
            return

        try:
            # Temporary resized video file names
            resized_files = [f"resized_video_{i}.mp4" for i in range(4)]

            # Resize all videos to 640x360
            for i, file_path in enumerate(file_paths):
                ffmpeg.input(file_path).filter('scale', 640, 360).output(resized_files[i]).run()

            # Merge videos into a 2x2 grid using the xstack filter
            grid_layout = "0_0|w0_0|0_h0|w0_h0"  # Arrange in 2x2 grid
            streams = [ffmpeg.input(resized_file) for resized_file in resized_files]
            ffmpeg.filter(streams, 'xstack', inputs=4, layout=grid_layout).output(output_file).run()

        except Exception as e:
            print(f"Error while exporting video: {e}")
        else:
            print(f"Merged video successfully exported to {output_file}.")
        finally:
            # Clean up temporary files
            for resized_file in resized_files:
                if os.path.exists(resized_file):
                    os.remove(resized_file)


    def play_pause_all_videos(self):
        for player in self.media_players:
            if player:
                if player.state() == QMediaPlayer.PlayingState:
                    player.pause()
                else:
                    player.play()

    def set_position(self, position):
        for player in self.media_players:
            if player:
                player.setPosition(position)

    def position_changed(self, position):
        # Update the slider position
        self.time_slider.setValue(position)

    def duration_changed(self, duration):
        # Update the slider range
        self.time_slider.setRange(0, duration)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = VideoSyncApp()
    eeg_paths = [None, None]
    # Passing paths if opened from editor
    if len(sys.argv) > 1:
        if len(sys.argv) <= 5:
            paths = sys.argv[1:]
        else:
            paths = sys.argv[1:5]
            eeg_paths = sys.argv[5:]

        for i, path in enumerate(paths):
            # Ignoring all 'skip' paths as there was no video there and loading others back to their space
            if path != "skip":
                ex.video_paths[i] = path
                ex.media_players[i] = vlc.MediaPlayer()
                ex.media_players[i].set_hwnd(int(ex.video_widgets[i].winId()))
                media = vlc.Media(path)
                ex.media_players[i].set_media(media)

                filename_label = getattr(ex, f"filename_{i + 1}")
                filename_label.setText(f"Filename:\n{path}")
                filename_label.setWordWrap(True)

        for eeg_path in eeg_paths:
            if eeg_path:
                # Add code to process eeg
                pass

    ex.show()
    sys.exit(app.exec_())
