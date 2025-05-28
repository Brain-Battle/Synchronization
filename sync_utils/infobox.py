from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QDialog,
    QGridLayout, QSlider, QCheckBox, QFileDialog, QDesktopWidget, QFrame, QSizePolicy
)
class Infobox(QWidget):
    def __init__(self, window_title: str = "Info", parent=None):
        super().__init__(parent)
        self.width = 480
        self.height = 100

        screen_geometry = QDesktopWidget().availableGeometry()
        screen_center_x = (screen_geometry.width() - self.width) // 2
        screen_center_y = (screen_geometry.height() - self.height) // 2
        self.setGeometry(screen_center_x, screen_center_y, self.width, self.height)

        self.setWindowTitle(window_title)

        layout = QVBoxLayout()
        self.label = QLabel("")
        layout.addWidget(self.label)
        self.setLayout(layout)

    def update_message(self, message: str):
        self.label.setText(message)
        self.label.setWordWrap(True)
        QApplication.processEvents()