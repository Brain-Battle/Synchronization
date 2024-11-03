from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
                             QGridLayout, QSlider, QCheckBox, QFileDialog, QDesktopWidget)
from PyQt5.QtCore import Qt
import sys

class VideoSyncApp(QWidget):
    def __init__(self):
        super().__init__()
        self.width = 1200
        self.height = 800
        # Preventing resizing of window (we know best shut up)
        self.setFixedSize(self.width, self.height)
        self.initUI()
        # Removing the maximise button functionality
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)

    def initUI(self):
        self.setWindowTitle('BattleUI')
        screen_geometry = QDesktopWidget().availableGeometry()

        # Calculate x, y position to center window
        screen_center_x = (screen_geometry.width() - self.width) // 2
        screen_center_y = (screen_geometry.height() - self.height) // 2
        self.setGeometry(screen_center_x, screen_center_y, self.width, self.height)

        main_layout = QVBoxLayout()

        # Create top layout for video panels and side upload buttons
        top_layout = QHBoxLayout()

        # Left Panel for Upload Buttons and Video Data
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

        # Right Panel for Upload Buttons and Video Data
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

        # Central Panel for Video Display Grid
        central_panel = QGridLayout()
        self.video_display_1 = QLabel()
        self.video_display_1.setFixedSize(400, 300)
        self.video_display_1.setStyleSheet("border: 1px solid black;")
        self.video_display_2 = QLabel()
        self.video_display_2.setFixedSize(400, 300)
        self.video_display_2.setStyleSheet("border: 1px solid black;")
        self.video_display_3 = QLabel()
        self.video_display_3.setFixedSize(400, 300)
        self.video_display_3.setStyleSheet("border: 1px solid black;")
        self.video_display_4 = QLabel()
        self.video_display_4.setFixedSize(400, 300)
        self.video_display_4.setStyleSheet("border: 1px solid black;")

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

        # EEG Data Display Box
        self.eeg_data_display = QLabel('EEG Data Display')
        self.eeg_data_display.setFixedHeight(50)
        self.eeg_data_display.setStyleSheet("border: 1px solid black;")

        bottom_panel.addWidget(self.eeg_data_display)
        bottom_panel.addLayout(slider_panel)

        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_panel)

        self.setLayout(main_layout)

    # Skeleton for button functionality for uploading videos
    def upload_video(self, video_num):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mov);;All Files (*)", options=options)
        if file_name:
            if video_num == 1:
                self.filename_1.setText(f'Filename\n{file_name}')
                self.filename_1.setWordWrap(True)
            elif video_num == 2:
                self.filename_2.setText(f'Filename\n{file_name}')
                self.filename_2.setWordWrap(True)
            elif video_num == 3:
                self.filename_3.setText(f'Filename\n{file_name}')
                self.filename_3.setWordWrap(True)
            elif video_num == 4:
                self.filename_4.setText(f'Filename\n{file_name}')
                self.filename_4.setWordWrap(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = VideoSyncApp()
    ex.show()
    sys.exit(app.exec_())
