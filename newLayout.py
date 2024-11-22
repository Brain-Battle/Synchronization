from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QStyle, QSlider, QFileDialog, QLabel, QFrame, QMessageBox, QSizePolicy, QSpacerItem
from PyQt5.QtGui import QPalette, QFont, QPainter, QColor
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl, QRect
from moviepy.editor import VideoFileClip
import sys
import os

# Custom QSlider for highlighting the mark-in and mark-out range
class HighlightSlider(QSlider):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.mark_in_position = 0
        self.mark_out_position = 0

    def set_marks(self, mark_in, mark_out):
        # Convert times from seconds to milliseconds (slider’s units)
        self.mark_in_position = int(mark_in * 1000)  
        self.mark_out_position = int(mark_out * 1000)
        self.update()  # Trigger a repaint to show the highlight

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.mark_in_position == 0 and self.mark_out_position == 0:
            return

        painter = QPainter(self)
        highlight_color = QColor(0, 150, 255, 100)  # Adjust transparency

        # Slider range
        slider_min = self.minimum()
        slider_max = self.maximum()

        # Map mark positions to the slider's pixel width
        mark_in_x = int((self.mark_in_position - slider_min) / (slider_max - slider_min) * self.width())
        mark_out_x = int((self.mark_out_position - slider_min) / (slider_max - slider_min) * self.width())

        # Draw highlighted rectangle between marks
        highlight_rect = QRect(mark_in_x, 0, mark_out_x - mark_in_x, self.height())
        painter.fillRect(highlight_rect, highlight_color)
        painter.end()

class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Media Player")
        self.setGeometry(600, 300, 700, 500)

        # Initialize variables for mark in and mark out times
        self.mark_in_time = None
        self.mark_out_time = None
        self.video_file = None

        # Initialize labels for current time and total duration
        self.currentTimeLabel = QLabel("00:00")
        self.totalDurationLabel = QLabel("00:00")

        self.create_player()

    def create_player(self):
        # Media player and video widget
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer.error.connect(self.handle_error)  # Connect error handling
        videoWidget = QVideoWidget()
        videoWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Set video widget to expand

        # Styled container frame for the video widget
        self.videoContainer = QFrame()
        self.videoContainer.setStyleSheet("""
        QFrame {
            background-color: light-grey;
            border: 2px solid;
            border-radius: 8px;
            padding: 5px;
        }
        """)
        self.videoContainer.setMinimumSize(640, 360)

        # Set the container frame to expand as well
        self.videoContainer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add videoWidget to videoContainer layout
        videoContainerLayout = QVBoxLayout(self.videoContainer)
        videoContainerLayout.setContentsMargins(0, 0, 0, 0)
        videoContainerLayout.addWidget(videoWidget)

        # Slider for video progress
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        # Custom slider with highlighting capability
        self.slider = HighlightSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        # Time display layout
        timeLayout = QHBoxLayout()
        timeLayout.addWidget(self.currentTimeLabel)
        timeLayout.addWidget(self.slider)
        timeLayout.addWidget(self.totalDurationLabel)

        # Buttons and Labels for controls
        self.playBtn = QPushButton()
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.setEnabled(False)
        self.playBtn.clicked.connect(self.play_video)
        self.playBtn.setMinimumSize(50, 40)
        self.playBtn.setMaximumSize(100, 50)

        # Vertical Volume Slider
        self.volumeSlider = QSlider(Qt.Vertical)
        self.volumeSlider.setRange(0, 100)  # Volume range: 0 to 100
        self.volumeSlider.setValue(50)  # Set default volume to 50%
        self.volumeSlider.valueChanged.connect(self.set_volume)  # Connect to volume control
        self.mediaPlayer.setVolume(50)  # Initialize media player volume

        # # Volume Slider
        # self.volumeSlider = QSlider(Qt.Horizontal)
        # self.volumeSlider.setRange(0, 100)  # Volume range: 0 to 100
        # self.volumeSlider.setValue(50)  # Set default volume to 50%
        # self.volumeSlider.valueChanged.connect(self.set_volume)  # Connect to volume control
        # self.mediaPlayer.setVolume(50)  # Initialize media player volume

        self.openBtn = QPushButton("Open Video file")
        self.openBtn.clicked.connect(self.open_file)
        self.openBtn.setMinimumSize(50, 40)
        self.openBtn.setMaximumSize(200, 50)

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

        # Video Container and Slider in the first layout
        VideoSlider = QVBoxLayout()
        VideoSlider.addWidget(self.videoContainer)
        VideoSlider.setStretch(0, 1)  # Allow video container to take as much space as possible
        VideoSlider.addLayout(timeLayout)

        # Left-side layout for volume slider
        leftSideLayout = QVBoxLayout()

        # Spacer to move the slider down
        spacer = QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed)  # Reduce height to 30
        leftSideLayout.addItem(spacer)  # Add spacer above the slider

        # Volume label
        volumeLabel = QLabel("Volume: ")
        # Align the label to the left
        leftSideLayout.addWidget(volumeLabel)

        # Volume slider
        leftSideLayout.addWidget(self.volumeSlider, alignment=Qt.AlignLeft)  # Align the slider to the left

        # Add volume slider and video controls side-by-side
        mainLayout = QHBoxLayout()
        # mainLayout.addLayout(leftSideLayout)  # Add volume slider to the left
        mainLayout.addLayout(VideoSlider)  # Add video container and controls to the right

        # Layout for play, open buttons
        controlLayout = QHBoxLayout()
        controlLayout.setSpacing(30)
        controlLayout.addWidget(self.openBtn, alignment=Qt.AlignLeft)
        controlLayout.addWidget(self.playBtn, alignment=Qt.AlignRight)

        # Vertical layout for mark in, mark out, cut, and save buttons
        markerLayout1 = QVBoxLayout()
        markerLayout1.setSpacing(15)
        markerLayout1.addWidget(self.markInBtn, alignment=Qt.AlignLeft)
        markerLayout1.addWidget(self.markInLabel, alignment=Qt.AlignLeft)

        markerLayout2 = QVBoxLayout()
        markerLayout2.setSpacing(15)
        markerLayout2.addWidget(self.markOutBtn, alignment=Qt.AlignCenter)
        markerLayout2.addWidget(self.markOutLabel, alignment=Qt.AlignCenter)

        markerLayout3 = QVBoxLayout()
        markerLayout3.setSpacing(15)
        markerLayout3.addWidget(self.cutBtn, alignment=Qt.AlignRight)
        markerLayout3.addWidget(self.saveBtn, alignment=Qt.AlignRight)
      
        # Second Vertical Layout
        hBox = QHBoxLayout()
        hBox.setSpacing(200)
        hBox.addLayout(markerLayout1)
        hBox.addLayout(markerLayout2)
        hBox.addLayout(markerLayout3)

        # Main vertical layout for video container and controls
        vbox = QVBoxLayout()
        vbox.setSpacing(30)
        vbox.addLayout(mainLayout)
        vbox.addLayout(controlLayout)
        vbox.addLayout(hBox)
        # vbox.addLayout(volumeLayout)  # Add the volume slider here

        # Set media player output
        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediastate_changed)
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)

        self.setLayout(vbox)

        # Apply custom styles
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""          
        QWidget {
            background-color: #f7f7f7;
            padding: 5px;
        }

        /* QPushButton Styles */
        QPushButton {
          background-color: white;
          color: black;
          padding: 10px 20px;
          font-size: 15px;
          font-weight: bold;
          border: 2px solid black; /* Set border width, style, and color */
          border-radius: 6px;
        }

        QPushButton:hover {
            background-color: light grey;
            color: black;
        }

        QPushButton:pressed {
            background-color: black;
            color: white;
        }

        /* QLabel Styles */
        QLabel {
            font-size: 15px;
            color: #333333;
            font-weight: 500;
            margin-bottom: 8px;
        }

        /* QSlider Styles */
        QSlider::groove:horizontal {
            border: 2px solid #aaaaaa;
            height: 10px;
            background: #cfcfcf;
            border-radius: 4px;
        }

        QSlider::handle:horizontal {
            background: grey;
            border: 2px solid black;
            width: 5px;
            height: 30px;
            margin: -5px 0;
            border-radius: 0px;
        }

        QSlider::handle:horizontal:hover {
            background-color: #45a049;
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
        # Update current time label
        self.currentTimeLabel.setText(self.format_time(position / 1000))

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)
        # Update total duration label
        self.totalDurationLabel.setText(self.format_time(duration / 1000))

    def set_position(self, position):
        self.mediaPlayer.setPosition(position)

    def place_mark_in(self):
        self.mark_in_time = self.mediaPlayer.position() / 1000
        self.markInLabel.setText(f"Mark In Time\n{self.format_time(self.mark_in_time)}")
        self.update_highlight()

    def place_mark_out(self):
        self.mark_out_time = self.mediaPlayer.position() / 1000
        self.markOutLabel.setText(f"Mark Out Time\n{self.format_time(self.mark_out_time)}")
        self.update_highlight()

    def update_highlight(self):
        if self.mark_in_time is not None and self.mark_out_time is not None:
            self.slider.set_marks(self.mark_in_time, self.mark_out_time)    

    def cut_in_out(self):
        message_box = QMessageBox(self)
        message_box.setWindowTitle("Message Alert")
        message_box.setIcon(QMessageBox.Information)
        if self.mark_in_time is None or self.mark_out_time is None:
            print("Please set both Mark In and Mark Out points.")
            message_box.setText("Please set both Mark In and Mark Out points.")
            message_box.setIcon(QMessageBox.Warning)
            message_box.exec()
            return
        if self.mark_out_time <= self.mark_in_time:
            print("Mark Out must be after Mark In.")
            message_box.setText("Mark Out must be after Mark In.")
            message_box.setIcon(QMessageBox.Critical)
            message_box.exec()
            return

        # Load video and create a cut clip
        self.clip = VideoFileClip(self.video_file).subclip(self.mark_in_time, self.mark_out_time)
        print("Clip cut successfully.")
        message_box.setText("Clip cut successfully.")
        message_box.exec()

        # Reset mark in and mark out values after successful cut
        self.mark_in_time = None
        self.mark_out_time = None
        self.markInLabel.setText("Mark In Time\n00:00")
        self.markOutLabel.setText("Mark Out Time\n00:00")

        # Clear the highlight on the slider by resetting marks
        self.slider.set_marks(0, 0)  # Set to no highlight
        self.slider.update()  # Force update to reflect changes

    def save_cut(self):
        message_box = QMessageBox(self)
        message_box.setWindowTitle("Message Alert")
        message_box.setIcon(QMessageBox.Information)
        if not hasattr(self, 'clip'):
            print("No cut clip available. Perform a cut first.")
            message_box.setText("No cut clip available. Perform a cut first.")
            message_box.setIcon(QMessageBox.Warning)
            message_box.exec()
            return

        save_filename, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Video Files (*.mp4)")

        if save_filename:
            self.clip.write_videofile(save_filename, codec='libx264')
            print("File saved successfully.")
            message_box.setText("File saved successfully.")
            message_box.exec()

    def format_time(self, seconds):
        mins, secs = divmod(int(seconds), 60)
        return f"{mins:02}:{secs:02}"
    
    def set_volume(self, value):
        """Set the media player's volume based on the slider value."""
        self.mediaPlayer.setVolume(value)

    def handle_error(self):
        """Handle media player errors."""
        error_code = self.mediaPlayer.error()
        error_message = self.mediaPlayer.errorString()

        if error_code == QMediaPlayer.ResourceError:
            error_message = (
                "The video file format might not be supported, "
                "or the necessary codec is not installed on your system. "
                "Please install the required codec and try again."
            )
        elif error_message == "":
            error_message = "An unknown error occurred while trying to play the media."    

        # Show an error message box
        message_box = QMessageBox(self)
        message_box.setWindowTitle("Playback Error")
        message_box.setIcon(QMessageBox.Critical)
        message_box.setText(error_message)
        message_box.exec()    

# Run the application
app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec_())
