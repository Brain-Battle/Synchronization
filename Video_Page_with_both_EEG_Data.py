import vlc
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
                             QGridLayout, QSlider, QCheckBox, QFileDialog, QDesktopWidget, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from datetime import datetime
import sys

class VideoSyncApp(QWidget):
    def __init__(self):
        super().__init__()
        self.width = 1200
        self.height = 800
        self.media_players = [None, None, None, None]
        self.video_widgets = [None, None, None, None]
        self.setFixedSize(self.width, self.height)
        self.initUI()
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)

        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_slider_position)
        self.timer.start()

    def initUI(self):
        self.setWindowTitle('BattleUI')
        screen_geometry = QDesktopWidget().availableGeometry()
        screen_center_x = (screen_geometry.width() - self.width) // 2
        screen_center_y = (screen_geometry.height() - self.height) // 2
        self.setGeometry(screen_center_x, screen_center_y, self.width, self.height)

        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()

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

        central_panel = QGridLayout()
        self.video_display_1 = QFrame()
        self.video_display_1.setFixedSize(400, 200)
        self.video_display_1.setStyleSheet("border: 2px solid black;")

        self.video_display_2 = QFrame()
        self.video_display_2.setFixedSize(400, 200)
        self.video_display_2.setStyleSheet("border: 2px solid black;")

        self.video_display_3 = QFrame()
        self.video_display_3.setFixedSize(400, 200)
        self.video_display_3.setStyleSheet("border: 2px solid black;")

        self.video_display_4 = QFrame()
        self.video_display_4.setFixedSize(400, 200)
        self.video_display_4.setStyleSheet("border: 2px solid black;")

        # EEG Plot Panel 1
        self.eeg_data_display_1 = QLabel('EEG Data Display 1')
        self.eeg_data_display_1 = QFrame()  # Use QFrame as a container
        self.eeg_data_display_1.setFixedSize(800, 150)
        self.eeg_data_display_1.setStyleSheet("border: 2px solid black;")
        self.eeg_plot_layout_1 = QVBoxLayout(self.eeg_data_display_1)

        # EEG Plot Panel 2
        self.eeg_data_display_2 = QLabel('EEG Data Display 2')
        self.eeg_data_display_2 = QFrame()  # Use QFrame as a container
        self.eeg_data_display_2.setFixedSize(800, 150)
        self.eeg_data_display_2.setStyleSheet("border: 2px solid black;")
        self.eeg_plot_layout_2 = QVBoxLayout(self.eeg_data_display_2)

        self.video_widgets = [self.video_display_1, self.video_display_2, self.video_display_3, self.video_display_4]

        central_panel.addWidget(self.video_display_1, 0, 0)
        central_panel.addWidget(self.video_display_2, 0, 1)
        central_panel.addWidget(self.video_display_3, 1, 0)
        central_panel.addWidget(self.video_display_4, 1, 1)

        top_layout.addLayout(left_panel)
        top_layout.addLayout(central_panel)
        top_layout.addLayout(right_panel)

        eeg_data_panel = QVBoxLayout()
        # # EEG Plot Panel
        # self.eeg_data_display = QLabel('EEG Data Display')
        # self.eeg_data_display = QFrame()  # Use QFrame as a container
        # self.eeg_data_display.setFixedSize(800, 200)
        # self.eeg_data_display.setStyleSheet("border: 2px solid black;")
        # self.eeg_plot_layout = QVBoxLayout(self.eeg_data_display)  # Layout for embedding EEG plots

        bottom_panel = QVBoxLayout()
        slider_panel = QHBoxLayout()
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setValue(0)
        self.time_slider.sliderReleased.connect(self.update_video_positions)
        slider_panel.addWidget(self.time_slider)

        self.timecode_checkbox = QCheckBox('Timecode')
        slider_panel.addWidget(self.timecode_checkbox)

        self.upload_eeg_btn_1 = QPushButton('Upload EEG 1')
        self.upload_eeg_btn_1.clicked.connect(self.upload_eeg_1)
        self.upload_eeg_btn_2 = QPushButton('Upload EEG 2')
        self.upload_eeg_btn_2.clicked.connect(self.upload_eeg_2)
        self.auto_sync_btn = QPushButton('Auto Sync')
        slider_panel.addWidget(self.upload_eeg_btn_1)
        slider_panel.addWidget(self.upload_eeg_btn_2)
        slider_panel.addWidget(self.auto_sync_btn)

        self.play_pause_btn = QPushButton('Play/Pause')
        self.play_pause_btn.clicked.connect(self.play_pause_all_videos)
        slider_panel.addWidget(self.play_pause_btn)

        eeg_data_panel.addWidget(self.eeg_data_display_1, alignment=Qt.AlignCenter)
        eeg_data_panel.addWidget(self.eeg_data_display_2, alignment=Qt.AlignCenter)

        bottom_panel.addLayout(slider_panel)

        main_layout.addLayout(top_layout)
        main_layout.addLayout(eeg_data_panel)
        main_layout.addLayout(bottom_panel)

        self.setLayout(main_layout)

    def upload_video(self, video_num):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Video File", "",
                                                   "Video Files (*.mp4 *.avi *.mov);;All Files (*)", options=options)
        if file_name:
            if not self.media_players[video_num - 1]:
                # Initialize VLC media player for this video
                self.media_players[video_num - 1] = vlc.MediaPlayer()
                self.media_players[video_num - 1].set_hwnd(int(self.video_widgets[video_num - 1].winId()))

            print(f"Attempting to load video {video_num} from: {file_name}")
            media = vlc.Media(file_name)
            self.media_players[video_num - 1].set_media(media)

            # Update the filename label
            filename_label = getattr(self, f"filename_{video_num}")
            filename_label.setText(f"Filename:\n{file_name}")
            filename_label.setWordWrap(True)


    def play_pause_all_videos(self):
        for player in self.media_players:
            if player:
                if player.is_playing():
                    player.pause()
                else:
                    player.play()

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

        fig, axs = plt.subplots(2, 2, sharex=True, sharey=False, layout="constrained")
        axs = axs.flatten()
        
        axs[0].plot(df["timestamps"], df["TP9"], color="blue", linewidth=2)
        axs[1].plot(df["timestamps"], df["AF7"], color="purple", linewidth=2)
        axs[2].plot(df["timestamps"], df["TP10"], color="cyan", linewidth=2)
        axs[3].plot(df["timestamps"], df["AF8"], color="pink", linewidth=2)
    
        for ax in axs:
            ax.legend(fontsize=5)
            ax.grid(True)

        fig.suptitle("EEG Plot 1", fontsize=8)

        if CONVERT_TO_DATETIME and PULL_TO_EPOCH:
            axs[-1].xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S.%f"))

        fig.tight_layout()

        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, self)
        toolbar.setFixedHeight(25)
        self.eeg_plot_layout_1.addWidget(toolbar)
        self.eeg_plot_layout_1.addWidget(canvas)

    def process_and_plot_eeg_2(self, file_name):
        CONVERT_TO_DATETIME = False
        PULL_TO_EPOCH = False

        df = pd.read_csv(file_name)

        if CONVERT_TO_DATETIME:
            initial_timestamp = df["timestamps"][0]
            df["timestamps"] = df["timestamps"].apply(lambda x: datetime.fromtimestamp(x - initial_timestamp))

        fig, axs = plt.subplots(2, 2, sharex=True, layout="constrained")
        axs = axs.flatten()

        axs[0].plot(df["timestamps"], df["TP9"], color="red", linewidth=2)
        axs[1].plot(df["timestamps"], df["AF7"], color="orange", linewidth=2)
        axs[2].plot(df["timestamps"], df["TP10"], color="green", linewidth=2)
        axs[3].plot(df["timestamps"], df["AF8"], color="blue", linewidth=2)

        for ax in axs:
            ax.legend(fontsize=5)
            ax.grid(True)

        fig.suptitle("EEG Plot 2", fontsize=8)

        if CONVERT_TO_DATETIME and PULL_TO_EPOCH:
            axs[-1].xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S.%f"))

        fig.tight_layout()

        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, self)
        toolbar.setFixedHeight(25)
        self.eeg_plot_layout_2.addWidget(toolbar)
        self.eeg_plot_layout_2.addWidget(canvas)       

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = VideoSyncApp()
    ex.show()
    sys.exit(app.exec_())

"""
TO-DO:
- Add functionality to EEG button, auto sync button, and timecode checkbox.
"""