import os
import ffmpeg
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QProgressBar, QStackedWidget, QTextBrowser, QMessageBox, QDesktopWidget
)
from PyQt5.QtCore import Qt, QTimer
import sys

class VideoSyncApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('VideoSyncApp')
        self.setGeometry(100, 100, 800, 600)

        # Main Layout
        main_layout = QVBoxLayout()

        # Help Button for Tutorial
        self.help_button = QPushButton("Help", self)
        self.help_button.clicked.connect(self.show_tutorial)
        main_layout.addWidget(self.help_button, alignment=Qt.AlignRight)

        # Auto-Process Button
        self.auto_process_button = QPushButton("Auto Process", self)
        self.auto_process_button.clicked.connect(self.auto_process)
        main_layout.addWidget(self.auto_process_button)

        # Progress Bar
        self.progress_bar = QProgressBar(self)
        main_layout.addWidget(self.progress_bar)

        # Status Label
        self.status_label = QLabel("Status: Ready", self)
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

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

    def auto_process(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Main Folder")
        if not folder_path:
            QMessageBox.warning(self, "Error", "No folder selected.")
            return

        subfolders = [os.path.join(folder_path, d) for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]
        total_subfolders = len(subfolders)

        if total_subfolders == 0:
            QMessageBox.warning(self, "Error", "No subfolders found in the selected directory.")
            return

        self.progress_bar.setMaximum(total_subfolders)

        for index, subfolder in enumerate(subfolders):
            self.status_label.setText(f"Processing folder: {subfolder}")
            QApplication.processEvents()

            # Process files in subfolder
            self.process_folder(subfolder)

            # Update progress bar
            self.progress_bar.setValue(index + 1)

        self.status_label.setText("Processing complete.")
        QMessageBox.information(self, "Success", "All folders have been processed.")

    def process_folder(self, folder_path):
        video_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.mp4', '.avi', '.mov'))]
        csv_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]

        if len(video_files) < 4 or len(csv_files) < 1:
            print(f"Insufficient files in {folder_path}. Skipping.")
            return

        # Assume the first CSV file for EEG processing
        eeg_file = csv_files[0]
        self.plot_eeg(eeg_file)

        # Merge videos (example implementation)
        output_video = os.path.join(folder_path, "merged_output.mp4")
        try:
            resized_files = [f"{folder_path}/resized_{i}.mp4" for i in range(4)]

            for i, video in enumerate(video_files[:4]):
                ffmpeg.input(video).filter('scale', 640, 360).output(resized_files[i]).run()

            grid_layout = "0_0|w0_0|0_h0|w0_h0"
            streams = [ffmpeg.input(file) for file in resized_files]
            ffmpeg.filter(streams, 'xstack', inputs=4, layout=grid_layout).output(output_video).run()

            print(f"Merged video saved to {output_video}")
        except Exception as e:
            print(f"Error processing folder {folder_path}: {e}")

        finally:
            # Clean up temporary resized files
            for file in resized_files:
                if os.path.exists(file):
                    os.remove(file)

    def plot_eeg(self, file_name):
        # Placeholder for EEG plotting function
        print(f"Plotting EEG data from {file_name}...")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = VideoSyncApp()
    ex.show()
    sys.exit(app.exec_())
