from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QStyle, QSlider, QFileDialog, QLabel, QFrame
from PyQt5.QtGui import QPalette, QFont
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl
from moviepy.editor import VideoFileClip
import sys
import os

class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Media Player")
        self.setGeometry(600, 300, 700, 500)

        # Initialize variables for mark in and mark out times
        self.mark_in_time = None
        self.mark_out_time = None
        self.video_file = None

        self.create_player()

    def create_player(self):
        # Media player and video widget
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        videoWidget = QVideoWidget()

        # Styled container frame for the video widget
        self.videoContainer = QFrame()
        self.videoContainer.setStyleSheet("""
        QFrame {
            background-color: light-grey;
            border: 2px solid;
            border-radius: 8px;
            padding: 5px; /* Space between border and video */
        }
        """)
        self.videoContainer.setMinimumSize(640, 360)  # Minimum width and height
        self.videoContainer.setMaximumSize(1000, 1000)  # Maximum width and height
        
        videoContainerLayout = QVBoxLayout(self.videoContainer)
        videoContainerLayout.setContentsMargins(0, 0, 0, 0)
        videoContainerLayout.addWidget(videoWidget)

        # Slider for video progress
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        # Buttons and Labels for controls
        self.playBtn = QPushButton()
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.setEnabled(False)
        self.playBtn.clicked.connect(self.play_video)
        self.playBtn.setMinimumSize(50, 40)  # Width: 150px, Height: 40px
        self.playBtn.setMaximumSize(100, 50)  # Width: 200px, Height: 50px

        self.openBtn = QPushButton("Open Video file")
        self.openBtn.clicked.connect(self.open_file)
        self.openBtn.setMinimumSize(50, 40)  # Width: 150px, Height: 40px
        self.openBtn.setMaximumSize(200, 50)  # Width: 200px, Height: 50px

        # Labels for time markers
        self.markInLabel = QLabel("Mark In Time\n00:00")
        self.markInLabel.setAlignment(Qt.AlignCenter)
        self.markOutLabel = QLabel("Mark Out Time\n00:00")
        self.markOutLabel.setAlignment(Qt.AlignCenter)

        # Buttons for time marking
        self.markInBtn = QPushButton("Place Mark In")
        self.markInBtn.clicked.connect(self.place_mark_in)
        self.markOutBtn = QPushButton("Place Mark Out")
        self.markOutBtn.clicked.connect(self.place_mark_out)
        self.cutBtn = QPushButton("Cut In-Out")
        self.cutBtn.clicked.connect(self.cut_in_out)
        self.saveBtn = QPushButton("Save")
        self.saveBtn.clicked.connect(self.save_cut)

        #Video Container and Slider in the first layout
        VideoSlider = QVBoxLayout()
        VideoSlider.addWidget(self.videoContainer, alignment=Qt.AlignCenter)
        VideoSlider.addWidget(self.slider)

        # Layout for play, open buttons
        controlLayout = QHBoxLayout()
        controlLayout.setSpacing(30)
        controlLayout.addWidget(self.openBtn, alignment=Qt.AlignLeft)
        controlLayout.addWidget(self.playBtn, alignment=Qt.AlignRight)

        # Vertical layout for mark in, mark out, cut, and save buttons
        markerLayout1 = QVBoxLayout()
        markerLayout1.setSpacing(15)  # Space between vertical items for alignment
        markerLayout1.addWidget(self.markInBtn)
        markerLayout1.addWidget(self.markInLabel)

        markerLayout2 = QVBoxLayout()
        markerLayout2.setSpacing(15)  # Space between vertical items for alignment
        markerLayout2.addWidget(self.markOutBtn)
        markerLayout2.addWidget(self.markOutLabel)

        markerLayout3 = QVBoxLayout()
        markerLayout3.setSpacing(15)  # Space between vertical items for alignment
        markerLayout3.addWidget(self.cutBtn)
        markerLayout3.addWidget(self.saveBtn)
      
        #Second Vertical Layout
        hBox = QHBoxLayout()
        hBox.setSpacing(200)
        hBox.addLayout(markerLayout1)
        hBox.addLayout(markerLayout2)
        hBox.addLayout(markerLayout3)

        # Main vertical layout for video container and controls
        vbox = QVBoxLayout()
        vbox.setSpacing(30)
        vbox.addLayout(VideoSlider)  # Add the container instead of the video widget directly
        vbox.addLayout(controlLayout)
        vbox.addLayout(hBox)

        # Set media player output
        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediastate_changed)
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)

        self.setLayout(vbox)  # Apply the final layout


        # Apply custom styles
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""          
            QWidget {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-size: 14px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                font-size: 14px;
                color: #333333;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #b3b3b3;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                border: 1px solid #4CAF50;
                width: 15px;
                margin: -2px 0;
                border-radius: 7px;
            }
        """)

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video")

        if filename != '':
            self.video_file = filename
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
            self.playBtn.setEnabled(True)

    def play_video(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediastate_changed(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def position_changed(self, position):
        self.slider.setValue(position)

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)

    def set_position(self, position):
        self.mediaPlayer.setPosition(position)

    def place_mark_in(self):
        self.mark_in_time = self.mediaPlayer.position() / 1000  # Store time in seconds
        self.markInLabel.setText(f"Mark In Time\n{self.format_time(self.mark_in_time)}")

    def place_mark_out(self):
        self.mark_out_time = self.mediaPlayer.position() / 1000  # Store time in seconds
        self.markOutLabel.setText(f"Mark Out Time\n{self.format_time(self.mark_out_time)}")

    def cut_in_out(self):
        if self.mark_in_time is None or self.mark_out_time is None:
            print("Please set both Mark In and Mark Out points.")
            return
        if self.mark_out_time <= self.mark_in_time:
            print("Mark Out must be after Mark In.")
            return

        # Load video and create a cut clip
        self.clip = VideoFileClip(self.video_file).subclip(self.mark_in_time, self.mark_out_time)
        print("Clip cut successfully.")

        # Reset mark in and mark out values after successful cut
        self.mark_in_time = None
        self.mark_out_time = None
        self.markInLabel.setText("Mark In Time\n00:00")
        self.markOutLabel.setText("Mark Out Time\n00:00")

    def save_cut(self):
        if not hasattr(self, 'clip'):
            print("No cut clip available. Perform a cut first.")
            return

        save_filename, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Video Files (*.mp4)")

        if save_filename:
            self.clip.write_videofile(save_filename, codec='libx264')
            print("File saved successfully.")

    def format_time(self, seconds):
        mins, secs = divmod(int(seconds), 60)
        return f"{mins:02}:{secs:02}"

# Run the application
app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec_())
