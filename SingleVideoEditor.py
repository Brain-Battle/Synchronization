from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QStyle, QSlider, QFileDialog, QLabel, QFrame, QMessageBox, QSizePolicy, QSpacerItem
from PyQt5.QtGui import QPalette, QFont, QPainter, QColor
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl, QRect
from moviepy import VideoFileClip
import sys

class HighlightSlider(QSlider):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.mark_in_position = 0
        self.mark_out_position = 0

    def set_mark_in(self, mark_in):
        self.mark_in_position = int(mark_in * 1000)
        self.update()

    def set_mark_out(self, mark_out):
        self.mark_out_position = int(mark_out * 1000)
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.mark_in_position == 0 and self.mark_out_position == 0:
            return

        painter = QPainter(self)
        highlight_color = QColor(0, 150, 255, 100)

        slider_min = self.minimum()
        slider_max = self.maximum()

        mark_in_x = int((self.mark_in_position - slider_min) / (slider_max - slider_min) * self.width())
        mark_out_x = int((self.mark_out_position - slider_min) / (slider_max - slider_min) * self.width())

        highlight_rect = QRect(mark_in_x, 0, mark_out_x - mark_in_x, self.height())
        painter.fillRect(highlight_rect, highlight_color)
        painter.end()

class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Media Player")
        self.setGeometry(600, 300, 700, 500)

        self.mark_in_time = None
        self.mark_out_time = None
        self.video_file = None

        self.currentTimeLabel = QLabel("00:00")
        self.totalDurationLabel = QLabel("00:00")

        self.create_player()

    def create_player(self):
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer.error.connect(self.handle_error)
        videoWidget = QVideoWidget()
        videoWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

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
        self.videoContainer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        videoContainerLayout = QVBoxLayout(self.videoContainer)
        videoContainerLayout.setContentsMargins(0, 0, 0, 0)
        videoContainerLayout.addWidget(videoWidget)

        self.slider = HighlightSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        timeLayout = QHBoxLayout()
        timeLayout.addWidget(self.currentTimeLabel)
        timeLayout.addWidget(self.slider)
        timeLayout.addWidget(self.totalDurationLabel)

        self.playBtn = QPushButton()
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.setEnabled(False)
        self.playBtn.clicked.connect(self.play_video)
        self.playBtn.setMinimumSize(50, 40)
        self.playBtn.setMaximumSize(100, 50)

        self.volumeSlider = QSlider(Qt.Vertical)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setValue(50)
        self.volumeSlider.valueChanged.connect(self.set_volume)
        self.mediaPlayer.setVolume(50)

        self.markInLabel = QLabel("Mark In Time\n00:00")
        self.markInLabel.setAlignment(Qt.AlignCenter)
        self.markOutLabel = QLabel("Mark Out Time\n00:00")
        self.markOutLabel.setAlignment(Qt.AlignCenter)

        self.markInBtn = QPushButton("Place Mark In")
        self.markInBtn.clicked.connect(self.place_mark_in)
        self.markOutBtn = QPushButton("Place Mark Out")
        self.markOutBtn.clicked.connect(self.place_mark_out)
        self.cutBtn = QPushButton("Cut In-Out")
        self.cutBtn.clicked.connect(self.cut_in_out)
        self.saveBtn = QPushButton("Save")
        self.saveBtn.clicked.connect(self.save_cut)

        VideoSlider = QVBoxLayout()
        VideoSlider.addWidget(self.videoContainer)
        VideoSlider.setStretch(0, 1)
        VideoSlider.addLayout(timeLayout)

        leftSideLayout = QVBoxLayout()
        spacer = QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed)
        leftSideLayout.addItem(spacer)
        volumeLabel = QLabel("Volume: ")
        leftSideLayout.addWidget(volumeLabel)
        leftSideLayout.addWidget(self.volumeSlider, alignment=Qt.AlignLeft)

        mainLayout = QHBoxLayout()
        mainLayout.addLayout(VideoSlider)

        controlLayout = QHBoxLayout()
        controlLayout.setSpacing(30)
        controlLayout.addWidget(self.playBtn, alignment=Qt.AlignRight)

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

        hBox = QHBoxLayout()
        hBox.setSpacing(200)
        hBox.addLayout(markerLayout1)
        hBox.addLayout(markerLayout2)
        hBox.addLayout(markerLayout3)

        vbox = QVBoxLayout()
        vbox.setSpacing(30)
        vbox.addLayout(mainLayout)
        vbox.addLayout(controlLayout)
        vbox.addLayout(hBox)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediastate_changed)
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)

        self.setLayout(vbox)
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""          
        QWidget {
            background-color: #f7f7f7;
            padding: 5px;
        }

        QPushButton {
          background-color: white;
          color: black;
          padding: 10px 20px;
          font-size: 15px;
          font-weight: bold;
          border: 2px solid black;
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

        QLabel {
            font-size: 15px;
            color: #333333;
            font-weight: 500;
            margin-bottom: 8px;
        }

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

    def open_file(self, filename):
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
        self.currentTimeLabel.setText(self.format_time(position / 1000))

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)
        self.totalDurationLabel.setText(self.format_time(duration / 1000))

    def set_position(self, position):
        self.mediaPlayer.setPosition(position)

    def set_volume(self, volume):
        self.mediaPlayer.setVolume(volume)

    def format_time(self, seconds):
        return '{:02}:{:02}'.format(int(seconds // 60), int(seconds % 60))

    def place_mark_in(self):
        if self.mediaPlayer.position() > 0:
            self.mark_in_time = self.mediaPlayer.position() / 1000
            self.markInLabel.setText(f"Mark In Time\n{self.format_time(self.mark_in_time)}")
            self.slider.set_mark_in(self.mark_in_time)

    def place_mark_out(self):
        if self.mediaPlayer.position() > 0:
            self.mark_out_time = self.mediaPlayer.position() / 1000
            self.markOutLabel.setText(f"Mark Out Time\n{self.format_time(self.mark_out_time)}")
            self.slider.set_mark_out(self.mark_out_time)

    def cut_in_out(self):
        if self.mark_in_time is not None and self.mark_out_time is not None:
            video = VideoFileClip(self.video_file)
            video = video.subclipped(self.mark_in_time, self.mark_out_time)
            video.write_videofile(paths[video_num], codec="libx264")

    def save_cut(self):
        if self.mark_in_time and self.mark_out_time:
            self.cut_in_out()

        QMessageBox.information(self, "Success", "Video saved successfully!", QMessageBox.Ok)
        app.quit()

    def handle_error(self):
        QMessageBox.critical(self, "Error", "An error occurred while loading the media file.", QMessageBox.Ok)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    args = sys.argv[1:]
    video_num = int(args[-1]) - 1
    paths= args[:-3]
    window.open_file(paths[video_num])
    sys.exit(app.exec_())
