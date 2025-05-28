import vlc
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox,
    QGridLayout, QSlider, QCheckBox, QFileDialog, QDesktopWidget, QFrame, QSizePolicy, QTextBrowser
)
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtCore import Qt, QTimer
import sys
import ffmpeg
import os
import subprocess
import pandas as pd
import numpy as np
import datetime

# Imports for preview and export
from sync_utils.audio_analysis import find_all_delays_with_pivot, find_all_durations
from sync_utils.video_sync import ( 
    generate_single_preview_optimized, generate_single_preview, 
    generate_grid_command, run_ffmpeg_subprocess 
)
from sync_utils.eeg_video_sync import compare_video_eeg, cut_video_from_start_end
from sync_utils.infobox import Infobox
import tempfile

from prototype import autosync
from newLayout import HighlightSlider

from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QDialog


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
        self.width = 1920
        self.height = 1080
        self.media_players = [None, None, None, None]
        self.video_widgets = [None, None, None, None]
        self.video_paths = [None, None, None, None]
        self.eeg_paths = [None, None]
        self.initUI()
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.start()

        self.temp_folder = tempfile.TemporaryDirectory() 
        self.temp_video_paths = []

        self.eeg_file_name_1 = None
        self.eeg_file_name_2 = None
        self.eeg_file_name_3 = None

        self._durations = []
        self._delays = []


    def initUI(self):
        self.setWindowTitle('BattleUI')
        self.setStyleSheet("background-color: #F3F3F1;")
        screen_geometry = QDesktopWidget().availableGeometry()
        screen_center_x = (screen_geometry.width() - self.width) // 2
        screen_center_y = (screen_geometry.height() - self.height) // 2
        self.setGeometry(screen_center_x, screen_center_y, self.width, self.height)
        self.setFixedSize(1920, 1080) #change this

        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()#

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
        self.eeg_data_display_1 = QFrame()  # Use QFrame as a container
        self.eeg_data_display_1.setFixedSize(800, 150)
        self.eeg_data_display_1.setStyleSheet("border: 2px solid black;")
        self.eeg_plot_layout_1 = QVBoxLayout(self.eeg_data_display_1)

        self.eeg_data_display_2 = QLabel('EEG Data Display 2')
        self.eeg_data_display_2 = QFrame()  # Use QFrame as a container
        self.eeg_data_display_2.setFixedSize(800, 150)
        self.eeg_data_display_2.setStyleSheet("border: 2px solid black;")
        self.eeg_plot_layout_2 = QVBoxLayout(self.eeg_data_display_2)

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

    
        timecode_select_panel = QVBoxLayout()

        self.timecode_label  = QLabel()
        self.timecode_label.setText("Which Video's Timecode?")
        timecode_select_panel.addWidget(self.timecode_label)
        self.timecode_select = QComboBox()
        self.timecode_select.addItem("Video 0 (Top-Left)")
        self.timecode_select.addItem("Video 1 (Top-Right)")
        self.timecode_select.addItem("Video 2 (Bottom-Left)")
        self.timecode_select.addItem("Video 3 (Bottom-Right)")
        self.timecode_select.addItem("No Selection")
        self.timecode_select.setCurrentIndex(4)
        timecode_select_panel.addWidget(self.timecode_select)
        slider_panel_2.addLayout(timecode_select_panel)

        self.upload_eeg_btn_1 = QPushButton('Upload EEG 1')
        self.upload_eeg_btn_1.clicked.connect(self.upload_eeg_1)
        self.upload_eeg_btn_1.setStyleSheet("background-color: #FFFFFF;")

        self.upload_eeg_btn_2 = QPushButton('Upload EEG 2')
        self.upload_eeg_btn_1.clicked.connect(self.upload_eeg_2)
        self.upload_eeg_btn_2.setStyleSheet("background-color: #FFFFFF;")

        self.auto_sync_btn = QPushButton('Auto Sync')
        self.auto_sync_btn.setStyleSheet("background-color: #FFFFFF;")
        self.auto_sync_btn.clicked.connect(self.auto_sync)

        self.auto_process_btn = QPushButton('Auto Process Folder')
        self.auto_process_btn.setStyleSheet("background-color: #FFFFFF;")
        self.auto_process_btn.clicked.connect(self.auto_process)

        slider_panel_2.addWidget(self.upload_eeg_btn_1)
        slider_panel_2.addWidget(self.upload_eeg_btn_2)
        slider_panel_2.addWidget(self.auto_sync_btn)
        slider_panel_2.addWidget(self.auto_process_btn)


        self.play_pause_btn = QPushButton('Play/Pause')
        self.play_pause_btn.setStyleSheet("background-color: #FFFFFF;")
        self.play_pause_btn.clicked.connect(self.play_pause_all_videos)
        slider_panel_2.addWidget(self.play_pause_btn)

        self.export_btn = QPushButton('Export')
        self.export_btn.setStyleSheet("background-color: #FFFFFF;")
        self.export_btn.clicked.connect(self.export)
        slider_panel_2.addWidget(self.export_btn)

        bottom_panel.addLayout(slider_panel)
        bottom_panel.addLayout(slider_panel_2)

        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_panel)

        self.setLayout(main_layout)

    def auto_sync(self):
        for path in self.video_paths:
            if path == None:
                print("Please input all videos.")
                return
        
        progress_dialog = Infobox("Auto-sync")
        progress_dialog.show()

        # Making a copy because we will mutate the list in a second
        video_paths = self.video_paths

        progress_dialog.update_message("Analyzing durations...")
        durations = find_all_durations(self.video_paths)

        # If index selected in timecode selector indicates none
        # set it to the video with longest duration
        if self.timecode_select.currentIndex() == 4:
            timecode_index = np.argmax(durations)
        else:
            timecode_index = self.timecode_select.currentIndex()

        video_preview_commands = []
        temp_output_paths = [None, None, None, None]

        # Process the longest video with EEG first
        # This step is skipped if there is no EEG data
        if self.eeg_file_name_1 != None or self.eeg_file_name_2 != None or self.eeg_file_name_3 != None:
            progress_dialog.update_message("EEG data detected. First synchronizing longest video with EEG.")
            
            if self.eeg_file_name_1:
                csv_file = self.eeg_file_name_1
            elif self.eeg_file_name_2:
                csv_file = self.eeg_file_name_2
            else:
                csv_file = self.eeg_file_name_3

            start_time, end_time = compare_video_eeg(self.video_paths[timecode_index], csv_file, durations[timecode_index])
            temp_name = f"temporary_eeg_sync_{datetime.datetime.now().strftime('%d%m%Y%H%M%S')}.mp4"
            temp_output_path = self.temp_folder.name + f"\\{temp_name}"

            progress_dialog.update_message(f"Synchronizing video {timecode_index} with EEG.")
            cut_video_from_start_end(self.video_paths[timecode_index], start_time, end_time, temp_output_path)

            video_paths[timecode_index] = temp_output_path
            durations[timecode_index] = end_time - start_time

        progress_dialog.update_message(f"Finding all delays by analyzing audios.")
        delays = find_all_delays_with_pivot(video_paths, timecode_index)
        max_delay = max(delays)
        
        for index, path in enumerate(video_paths):
            temp_name = f"temporary_vid_{datetime.datetime.now().strftime('%d%m%Y%H%M%S')}_{index}.mp4"
            temp_output_path = self.temp_folder.name + f"\\{temp_name}"
            progress_dialog.update_message(f"Generating command for video {index}.")
            command, new_duration = generate_single_preview(path, delays[index], durations[index], temp_output_path, max_delay)

            temp_output_paths[index] = temp_output_path
            video_preview_commands.append(command)
            durations[index] = new_duration

        for index, command in enumerate(video_preview_commands):
            progress_dialog.update_message(f"Processing video {index}...")
            run_ffmpeg_subprocess(command, durations[index], debug=True)

        self.temp_video_paths = temp_output_paths

        new_medias = [QMediaContent(QUrl.fromLocalFile(path)) for path in self.temp_video_paths]

        for index, player in enumerate(self.media_players):
            player.setMedia(new_medias[index]) 
            player.positionChanged.connect(self.position_changed)
            player.durationChanged.connect(self.duration_changed)

        self._durations = durations
        self._delays = delays
        print(self._delays)

        progress_dialog.update_message(f"Auto-sync complete.")

        progress_dialog.close()

        print("Ready to export.")

    def export(self):
        output_file = QFileDialog.getSaveFileName(
            self, "Save Merged Video", "", "Video Files (*.mp4 *.avi *.mov);;All Files (*)")[0]
        if not output_file:
            return
        
        null_media = QMediaContent(None)

        self.media_players = [player.setMedia(null_media) for player in self.media_players]

        export_command, final_duration = generate_grid_command(self.temp_video_paths, self._delays, self._durations, 
                                                     output_file_name_with_extension=output_file)
        
        # Buggin
        print("FFMPEG Export Command:", export_command)

        run_ffmpeg_subprocess(export_command, final_duration, debug=True)

    def auto_process(self):
        """
            Processes a full folder of videos.

            Arguments
            - 
            
            Returns
            - 
            
        """
        folder_path = QFileDialog.getExistingDirectory(self, "Select Main Folder")
        if not folder_path:
            QMessageBox.warning(self, "Error", "No folder selected.")
            return

        infobox = Infobox("Auto Folder Processing")
        infobox.show()

        subfolders = [os.path.join(folder_path, d) for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]
        total_subfolders = len(subfolders)

        if total_subfolders == 0:
            infobox.close()
            QMessageBox.warning(self, "Error", "No subfolders found in the selected directory.")
            return

        for index, subfolder in enumerate(subfolders):
            QApplication.processEvents()

            infobox.update_message(f"Processing subfolder {subfolder}")

            # Process files in subfolder
            self.process_folder(subfolder)

        
        infobox.close()

        QMessageBox.information(self, "Success", "All folders have been processed.")

    def process_folder(self, folder_path):
        infobox = Infobox(f"Processing Folder {os.path.basename(folder_path)}")
        infobox.show()
        video_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.mp4', '.avi', '.mov', '.MP4', '.AVI', '.MOV'))]
        csv_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.csv', ".CSV"))]

        if len(video_files) < 4 or len(csv_files) < 1:
            infobox.close()
            print(f"Insufficient files in {folder_path}. Skipping.")
            return
        
        video_files = sorted(video_files)

        # Assume the first CSV file for EEG processing
        eeg_file = csv_files[0]

        infobox.update_message("Finding the durations of the video.")
        durations = find_all_durations(video_files)

        # We take longest video as basis
        timecode_index = np.argmax(durations)

        infobox.update_message("Syncing EEG with the longest video.")
        start_time, end_time = compare_video_eeg(video_files[timecode_index], eeg_file, durations[timecode_index])

        temp_name = f"temporary_eeg_sync_{datetime.datetime.now().strftime('%d%m%Y%H%M%S')}.mp4"
        temp_output_path = self.temp_folder.name + f"\\{temp_name}"

        cut_video_from_start_end(video_files[timecode_index], start_time, end_time, temp_output_path)
        
        video_files[timecode_index] = temp_output_path
        
        infobox.update_message("Finding all delays.")
        delays = find_all_delays_with_pivot(video_files, timecode_index)
        max_delay = max(delays)

        temp_output_paths = [None, None, None, None] 
        video_process_commands = []

        for index, path in enumerate(video_files):
            temp_name = f"temporary_vid_{datetime.datetime.now().strftime('%d%m%Y%H%M%S')}_{index}.mp4"
            temp_output_path = self.temp_folder.name + f"\\{temp_name}"
            command, new_duration = generate_single_preview(path, delays[index], durations[index], temp_output_path, max_delay)

            temp_output_paths[index] = temp_output_path
            video_process_commands.append(command)
            durations[index] = new_duration

        for index, command in enumerate(video_process_commands):
            infobox.update_message(f"Processing video {index}.")
            run_ffmpeg_subprocess(command, durations[index], debug=True)

        output_name = f"{os.path.basename(folder_path)}.mp4"

        infobox.update_message("Exporting the result.")
        export_command, final_duration = generate_grid_command(temp_output_paths, delays, durations, 
                                                     output_file_name_with_extension=output_name)
        
        run_ffmpeg_subprocess(export_command, final_duration)


    def upload_eeg_1(self):
        # File dialog to select the EEG CSV file
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open EEG File", "", "CSV Files (*.csv);;All Files (*)", options=options
        )
        if file_name:
            self.process_and_plot_eeg_1(file_name)
            self.eeg_file_name_1 = file_name

    def upload_eeg_2(self):
        # File dialog to select the EEG CSV file
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open EEG File", "", "CSV Files (*.csv);;All Files (*)", options=options
        )
        if file_name:
            self.process_and_plot_eeg_2(file_name)        
            self.eeg_file_name_2 = file_name

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

    def clean_up_temp(self):
        self.temp_folder.cleanup()

    def show_tutorial(self):
        tutorial_window = QWidget()
        tutorial_window.setWindowTitle("App Tutorial")
        tutorial_window.setGeometry(150, 150, 600, 400)

        layout = QVBoxLayout()

        tutorial_text = QTextBrowser()
        tutorial_text.setText(
            """
            <h1>Welcome to VideoSyncApp Tutorial</h1>
            <p>1. <b>Upload Videos:</b> Use the 'Upload' buttons to add your videos.</p>
            <p>2. <b>Edit Videos:</b> Click 'Edit' for trimming or resizing options.</p>
            <p>3. <b>EEG Processing:</b> Upload EEG CSV files for visualization.</p>
            <p>4. <b>Auto Process:</b> Organize your videos and EEG files in a folder structure, and let the app process them automatically.</p>
            <p>5. <b>Export:</b> Use the 'Export' button to save merged videos and EEG data.</p>
            """
        )
        layout.addWidget(tutorial_text)

        close_button = QPushButton("Close", tutorial_window)
        close_button.clicked.connect(tutorial_window.close)
        layout.addWidget(close_button)

        tutorial_window.setLayout(layout)
        tutorial_window.show()


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
