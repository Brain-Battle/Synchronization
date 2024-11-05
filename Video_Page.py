from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
                             QGridLayout, QSlider, QCheckBox, QFileDialog, QDesktopWidget, QFrame)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl
import sys

class VideoSyncApp(QWidget):
    def __init__(self):
        super().__init__()
        self.width = 1200
        self.height = 800
        self.setFixedSize(self.width, self.height)
        self.initUI()
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)

    def initUI(self):
        self.setWindowTitle('BattleUI')
        screen_geometry = QDesktopWidget().availableGeometry()

        screen_center_x = (screen_geometry.width() - self.width) // 2
        screen_center_y = (screen_geometry.height() - self.height) // 2
        self.setGeometry(screen_center_x, screen_center_y, self.width, self.height)

        main_layout = QVBoxLayout()

        top_layout = QHBoxLayout()

        # Left Panel for Upload Buttons and Video Data
        left_panel = QVBoxLayout()
        self.setup_video_controls(left_panel, 1)
        self.setup_video_controls(left_panel, 3)

        # Right Panel for Upload Buttons and Video Data
        right_panel = QVBoxLayout()
        self.setup_video_controls(right_panel, 2)
        self.setup_video_controls(right_panel, 4)

        # Central Panel for Video Display Grid
        central_panel = QGridLayout()
        self.video_display_1 = self.create_video_display()
        self.video_display_2 = self.create_video_display()
        self.video_display_3 = self.create_video_display()
        self.video_display_4 = self.create_video_display()

        central_panel.addWidget(self.video_display_1, 0, 0)
        central_panel.addWidget(self.video_display_2, 0, 1)
        central_panel.addWidget(self.video_display_3, 1, 0)
        central_panel.addWidget(self.video_display_4, 1, 1)

        top_layout.addLayout(left_panel)
        top_layout.addLayout(central_panel)
        top_layout.addLayout(right_panel)

        # Bottom Panel for Timecode, EEG Display, and Buttons
        bottom_panel = QVBoxLayout()
        slider_panel = QHBoxLayout()
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setValue(0)
        slider_panel.addWidget(self.time_slider)

        self.timecode_checkbox = QCheckBox('Timecode')
        slider_panel.addWidget(self.timecode_checkbox)

        self.upload_eeg_btn = QPushButton('Upload EEG')
        self.auto_sync_btn = QPushButton('Auto Sync')
        slider_panel.addWidget(self.upload_eeg_btn)
        slider_panel.addWidget(self.auto_sync_btn)

        self.eeg_data_display = QLabel('EEG Data Display')
        self.eeg_data_display.setFixedHeight(50)
        self.eeg_data_display.setStyleSheet("border: 1px solid black;")

        bottom_panel.addWidget(self.eeg_data_display)
        bottom_panel.addLayout(slider_panel)

        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_panel)

        self.setLayout(main_layout)

    def create_video_display(self):
        """Creates a QFrame containing a QVideoWidget for video playback."""
        video_container = QFrame()
        video_container.setFixedSize(400, 300)
        video_container.setStyleSheet("border: 1px solid black;")

        # Video Widget
        video_widget = QVideoWidget(video_container)
        video_layout = QVBoxLayout(video_container)
        video_layout.setContentsMargins(0, 0, 0, 0)
        video_layout.addWidget(video_widget)

        return video_container

    def setup_video_controls(self, layout, video_num):
        """Sets up upload button, filename label, and video data label for a specific video."""
        video_data = QLabel(f'Video Data {video_num}\n00:00')
        filename_label = QLabel('Filename')
        upload_button = QPushButton(f'Upload Video {video_num}')

        # Setup individual media players for each video
        media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        # Assign the media player and button to open the file
        upload_button.clicked.connect(lambda: self.open_video_file(media_player, video_num, filename_label))

        layout.addWidget(video_data)
        layout.addWidget(filename_label)
        layout.addWidget(upload_button)

    def open_video_file(self, media_player, video_num, filename_label):
        """Opens video file dialog and assigns selected video to the media player."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Video File", "",
                                                   "Video Files (*.mp4 *.avi *.mov);;All Files (*)")
        if file_name:
            filename_label.setText(f'Filename\n{file_name}')
            media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_name)))
            # Auto-play or set up additional playback controls here as needed


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = VideoSyncApp()
    ex.show()
    sys.exit(app.exec_())
