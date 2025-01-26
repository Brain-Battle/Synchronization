import vlc
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QSlider, QCheckBox, QFileDialog, QDesktopWidget, QFrame, QSizePolicy, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
import sys
import ffmpeg
import os


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

        # Video 1
        self.video_data_1 = QLabel('Video Data\n00:00')
        self.filename_1 = QLabel('Filename')
        self.upload_btn_1 = QPushButton('Upload Video 1')
        self.upload_btn_1.setStyleSheet("background-color: #FFFFFF;")
        self.upload_btn_1.clicked.connect(lambda: self.upload_video(1))
        left_panel.addWidget(self.video_data_1)
        left_panel.addWidget(self.filename_1)
        left_panel.addWidget(self.upload_btn_1)

        # Video 3
        self.video_data_3 = QLabel('Video Data\n00:00')
        self.filename_3 = QLabel('Filename')
        self.upload_btn_3 = QPushButton('Upload Video 3')
        self.upload_btn_3.setStyleSheet("background-color: #FFFFFF;")
        self.upload_btn_3.clicked.connect(lambda: self.upload_video(3))
        left_panel.addWidget(self.upload_btn_3)
        left_panel.addWidget(self.video_data_3)
        left_panel.addWidget(self.filename_3)

        # Right panel with buttons for Video 2 (top) and Video 4 (bottom)
        right_panel = QVBoxLayout()

        # Video 2
        self.video_data_2 = QLabel('Video Data\n00:00')
        self.filename_2 = QLabel('Filename')
        self.upload_btn_2 = QPushButton('Upload Video 2')
        self.upload_btn_2.setStyleSheet("background-color: #FFFFFF;")
        self.upload_btn_2.clicked.connect(lambda: self.upload_video(2))
        right_panel.addWidget(self.video_data_2)
        right_panel.addWidget(self.filename_2)
        right_panel.addWidget(self.upload_btn_2)

        # Video 4
        self.video_data_4 = QLabel('Video Data\n00:00')
        self.filename_4 = QLabel('Filename')
        self.upload_btn_4 = QPushButton('Upload Video 4')
        self.upload_btn_4.setStyleSheet("background-color: #FFFFFF;")
        self.upload_btn_4.clicked.connect(lambda: self.upload_video(4))
        right_panel.addWidget(self.upload_btn_4)
        right_panel.addWidget(self.video_data_4)
        right_panel.addWidget(self.filename_4)

        # Central panel for video displays
        central_panel = QGridLayout()
        self.video_display_1 = AspectRatioFrame(self)
        self.video_display_2 = AspectRatioFrame(self)
        self.video_display_3 = AspectRatioFrame(self)
        self.video_display_4 = AspectRatioFrame(self)
        self.video_widgets = [self.video_display_1, self.video_display_2, self.video_display_3, self.video_display_4]
        central_panel.addWidget(self.video_display_1, 0, 0)
        central_panel.addWidget(self.video_display_2, 0, 1)
        central_panel.addWidget(self.video_display_3, 1, 0)
        central_panel.addWidget(self.video_display_4, 1, 1)

        top_layout.addLayout(left_panel, 1)
        top_layout.addLayout(central_panel, 5)
        top_layout.addLayout(right_panel, 1)

        bottom_panel = QVBoxLayout()
        self.export_btn = QPushButton('Export')
        self.export_btn.setStyleSheet("background-color: #FFFFFF;")
        self.export_btn.clicked.connect(self.merge_videos)
        bottom_panel.addWidget(self.export_btn)

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
                self.show_error(f"Video {i} has not been loaded.")
                return

        # Check if all four videos are loaded
        if len(file_paths) != 4:
            self.show_error("Please load all four videos before exporting.")
            return

        # Output file name
        output_file = QFileDialog.getSaveFileName(
            self, "Save Merged Video", "", "Video Files (*.mp4 *.avi *.mov);;All Files (*)"
        )[0]
        if not output_file:
            return

        try:
            resized_files = [f"resized_video_{i}.mp4" for i in range(4)]
            for i, file_path in enumerate(file_paths):
                ffmpeg.input(file_path).filter('scale', 640, 360).output(resized_files[i]).run()

            ffmpeg.concat(*[ffmpeg.input(f) for f in resized_files], v=1, a=1).output(output_file).run()

        except Exception as e:
            self.show_error(f"An error occurred while merging videos: {str(e)}")

    def show_error(self, message):
        error_box = QMessageBox(self)
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle("Error")
        error_box.setText(message)
        error_box.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoSyncApp()
    player.show()
    sys.exit(app.exec_())
