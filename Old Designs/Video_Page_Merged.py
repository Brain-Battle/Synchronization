import vlc
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
                             QGridLayout, QSlider, QCheckBox, QFileDialog, QDesktopWidget, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import Qt, QTimer
import sys
import ffmpeg
import os
import VideoMerger.Videomerger as merger
import datetime
import pandas as pd

class AspectRatioFrame(QFrame):
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
        self.initUI()
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_slider_position)
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
        self.video_display_1.setMaximumSize(600, 338)

        self.video_display_2 = AspectRatioFrame(self)
        self.video_display_2.resize(400, 225)
        self.video_display_2.setStyleSheet("border: 1px solid black; box-sizing: border-box;")
        self.video_display_2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_display_2.setMaximumSize(600, 338)

        self.video_display_3 = AspectRatioFrame(self)
        self.video_display_3.resize(400, 225)
        self.video_display_3.setStyleSheet("border: 1px solid black; box-sizing: border-box;")
        self.video_display_3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_display_3.setMaximumSize(600, 338)

        self.video_display_4 = AspectRatioFrame(self)
        self.video_display_4.resize(400, 225)
        self.video_display_4.setStyleSheet("border: 1px solid black; box-sizing: border-box;")
        self.video_display_4.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_display_4.setMaximumSize(600, 338)

        self.video_widgets = [self.video_display_1, self.video_display_2, self.video_display_3, self.video_display_4]

        # EEG Plot Panel 1
        self.eeg_data_display_1 = QLabel('EEG Data Display 1')
        self.eeg_data_display_1 = QFrame()  # Use QFrame as a container
        self.eeg_data_display_1.setFixedSize(600, 250)
        self.eeg_data_display_1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.eeg_data_display_1.setStyleSheet("border: 2px solid black;")
        self.eeg_plot_layout_1 = QVBoxLayout(self.eeg_data_display_1)

        # EEG Plot Panel 2
        self.eeg_data_display_2 = QLabel('EEG Data Display 2')
        self.eeg_data_display_2 = QFrame()  # Use QFrame as a container
        self.eeg_data_display_2.setFixedSize(600, 250)
        self.eeg_data_display_2.setStyleSheet("border: 2px solid black;")
        self.eeg_plot_layout_2 = QVBoxLayout(self.eeg_data_display_2)

        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setValue(0)
        self.time_slider.sliderReleased.connect(self.update_video_positions)

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
        self.upload_eeg_btn_1.clicked.connect(self.upload_eeg_1)
        self.upload_eeg_btn_2 = QPushButton('Upload EEG 2')
        self.upload_eeg_btn_2.clicked.connect(self.upload_eeg_2)
        self.upload_eeg_btn_1.setStyleSheet("background-color: #FFFFFF;")
        self.upload_eeg_btn_2.setStyleSheet("background-color: #FFFFFF;")

        self.auto_sync_btn = QPushButton('Auto Sync')
        self.auto_sync_btn.setStyleSheet("background-color: #FFFFFF;")

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

    def upload_video(self, video_num):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Video File", "",
                                                   "Video Files (*.mp4 *.avi *.mov);;All Files (*)", options=options)
        if file_name:
            self.video_paths[video_num - 1] = file_name
            if not self.media_players[video_num - 1]:
                self.media_players[video_num - 1] = vlc.MediaPlayer()
                self.media_players[video_num - 1].set_hwnd(int(self.video_widgets[video_num - 1].winId()))

            media = vlc.Media(file_name)
            self.media_players[video_num - 1].set_media(media)

            filename_label = getattr(self, f"filename_{video_num}")
            filename_label.setText(f"Filename:\n{file_name}")
            filename_label.setWordWrap(True)

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
            producer = merger.VideoMerger()
            producer.video_input(file_paths[0], 0, 0)
            producer.video_input(file_paths[1], 0, 1)
            producer.video_input(file_paths[2], 1, 0)
            producer.video_input(file_paths[3], 1, 1)
            producer.export(output_file, threads=4)

        except Exception as e:
            print(f"Error while exporting video: {e}")
        else:
            print(f"Merged video successfully exported to {output_file}.")


    def play_pause_all_videos(self):
        for player in self.media_players:
            if player:
                if player.is_playing():
                    player.pause()
                else:
                    player.play()

    def upload_eeg_1(self):
        # File dialog to select the EEG CSV file
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open EEG File", "", "CSV Files (*.csv);;All Files (*)", options=options
        )
        if file_name:
            self.process_and_plot_eeg_1(file_name)

    def upload_eeg_2(self):
        # File dialog to select the EEG CSV file
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open EEG File", "", "CSV Files (*.csv);;All Files (*)", options=options
        )
        if file_name:
            self.process_and_plot_eeg_2(file_name)   


    def process_and_plot_eeg_1(self, file_name):
        CONVERT_TO_DATETIME = False
        PULL_TO_EPOCH = False

        df = pd.read_csv(file_name)

        if CONVERT_TO_DATETIME:
            initial_timestamp = df["timestamps"][0]
            df["timestamps"] = df["timestamps"].apply(lambda x: datetime.fromtimestamp(x - initial_timestamp))

        fig, axs = plt.subplots(4, 1, sharex=True, sharey=False, layout="constrained")
        axs = axs.flatten()
        
        axs[0].plot(df["timestamps"], df["TP9"], color="blue", linewidth=1)
        axs[1].plot(df["timestamps"], df["AF7"], color="purple", linewidth=1)
        axs[2].plot(df["timestamps"], df["TP10"], color="cyan", linewidth=1)
        axs[3].plot(df["timestamps"], df["AF8"], color="pink", linewidth=1)
    
        for ax in axs:
            ax.legend(fontsize=5)
            ax.grid(True)

        fig.suptitle("EEG Plot 1", fontsize=8)

        if CONVERT_TO_DATETIME and PULL_TO_EPOCH:
            axs[-1].xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S.%f"))

        fig.tight_layout()

        canvas = FigureCanvas(fig)
        self.eeg_plot_layout_1.addWidget(canvas)

    def update_video_positions(self):
        position_percentage = self.time_slider.value() / 100
        for player in self.media_players:
            if player and player.get_length() > 0:
                new_position = int(player.get_length() * position_percentage)
                player.set_time(new_position)

    def update_slider_position(self):
        for index, player in enumerate(self.media_players):
            if player and player.get_length() > 0:
                current_time = player.get_time()
                total_length = player.get_length()

                # Pause the video if it is within 200 milliseconds of the end
                if total_length - current_time <= 200:
                    print(f"Video {index + 1} is nearing the end. Pausing to prevent end state.")
                    player.pause()

                    # Rewind slightly to prevent end state and ensure responsiveness
                    player.set_time(total_length - 500)  # Rewind 500 milliseconds from the end

                # Update the slider position
                if total_length > 0:
                    slider_value = int((current_time / total_length) * 100)
                    self.time_slider.blockSignals(True)
                    self.time_slider.setValue(slider_value)
                    self.time_slider.blockSignals(False)


    def process_and_plot_eeg_2(self, file_name):
        CONVERT_TO_DATETIME = False
        PULL_TO_EPOCH = False

        df = pd.read_csv(file_name)

        if CONVERT_TO_DATETIME:
            initial_timestamp = df["timestamps"][0]
            df["timestamps"] = df["timestamps"].apply(lambda x: datetime.fromtimestamp(x - initial_timestamp))

        fig, axs = plt.subplots(4, 1, sharex=True, layout="constrained")
        axs = axs.flatten()

        axs[0].plot(df["timestamps"], df["TP9"], color="red", linewidth=1)
        axs[1].plot(df["timestamps"], df["AF7"], color="orange", linewidth=1)
        axs[2].plot(df["timestamps"], df["TP10"], color="green", linewidth=1)
        axs[3].plot(df["timestamps"], df["AF8"], color="blue", linewidth=1)

        for ax in axs:
            ax.legend(fontsize=5)
            ax.grid(True)

        fig.suptitle("EEG Plot 2", fontsize=8)

        if CONVERT_TO_DATETIME and PULL_TO_EPOCH:
            axs[-1].xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S.%f"))

        fig.tight_layout()

        canvas = FigureCanvas(fig)
        self.eeg_plot_layout_2.addWidget(canvas)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = VideoSyncApp()
    ex.show()
    sys.exit(app.exec_())


# Audio analysis libraries
# - Find the time difference between video clips via their audio.
# Synchronizing videos
# The edit video button
# Bakhshi & Stef

# EEG Data Progress Bar
# Muhammad

# Error handling
# Documentation
# Popup errors/warnings/info
# Aryan & Yasin