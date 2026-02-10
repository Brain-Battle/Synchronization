"""
Unified Camera and EEG Dashboard.

Connects to:
- 2x Insta360 cameras via USB (Media Foundation)
- 2x Muse S headbands via Bluetooth (LSL)

Displays:
- Top row: Camera feeds side by side
- Bottom row: Real-time EEG graphs for each user

Usage:
  python -m live_data_flow.live_mixed
"""

import multiprocessing
import threading
import queue
import time
import sys
import os
import numpy as np
import cv2
from pylsl import StreamInlet, resolve_byprop

# Re-use our robust camera reader
from live_data_flow.live_insta360 import CameraReader, find_cameras


class VideoLooper:
    """Loops a video file continuously."""
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.cap = cv2.VideoCapture(filepath)
        if not self.cap.isOpened():
            print(f"ERROR: Could not open video file: {filepath}")
        else:
             print(f"Loaded video: {filepath}")
    
    def get_frame(self):
        if not self.cap.isOpened():
            # Return static black frame with error text
            img = np.zeros((200, 640, 3), dtype=np.uint8)
            cv2.putText(img, "File Not Found", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
            return img

        ret, frame = self.cap.read()
        if not ret:
            # Loop
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
        
        if ret and frame is not None:
            return frame
        else:
            return None

    def release(self):
        self.cap.release()


def find_cameras_robust(max_index: int = 10, retries: int = 3) -> list[int]:
    """Find working cameras, skipping index 0 (internal). Retries on failure."""
    found = []
    # Skip index 0 explicitly
    for idx in range(1, max_index):
        for attempt in range(retries):
            cap = cv2.VideoCapture(idx, cv2.CAP_MSMF)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                if ret and frame is not None:
                    found.append(idx)
                    break 
            else:
                cap.release()
            # If failed, retry after short sleep if needed? 
            # Usually iterating indices is fast.
    return found

def main():
    # Parse args for video paths
    video_paths = []
    if len(sys.argv) > 1:
        # Assume args are video paths
        video_paths = sys.argv[1:]
    
    if len(video_paths) < 2:
        print("WARNING: Please provide paths to 2 video files for the EEG placeholders.")
        print("Usage: python -m live_data_flow.live_mixed path/to/eeg1.mp4 path/to/eeg2.mp4")
        # Generate fake paths if none provided, user will see "File Not Found"
        if not video_paths:
            video_paths = ["eeg1.mp4", "eeg2.mp4"]
        elif len(video_paths) == 1:
            video_paths.append("eeg2.mp4")

    # 1. Detect Cameras
    print("--- Detecting Cameras ---")
    cam_indices = find_cameras_robust()
    
    if len(cam_indices) < 2:
        print(f"WARNING: Need 2 external cameras, found {len(cam_indices)}: {cam_indices}")
    else:
        print(f"  Found cameras at indices: {cam_indices}")

    # 2. Setup Video Loopers
    print("\n--- Setting up Video Playback ---")
    video_loopers = []
    for path in video_paths[:2]:
        video_loopers.append(VideoLooper(path))

    # 3. Start Camera Readers
    cam_readers = []
    
    print("\n--- Selecting Cameras (Skipping Index 0) ---")
    for idx in cam_indices:
        print(f"Checking camera at index {idx}...")
        cr = CameraReader(idx)
        if cr.is_ready:
            # Check resolution
            w = int(cr.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cr.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            if w >= 1920 and h >= 1080:
                print(f"  -> Accepted (Resolution: {w}x{h})")
                cr.start()
                cam_readers.append(cr)
            else:
                print(f"  -> Skipped (Resolution: {w}x{h} < 1080p)")
                cr.stop()
        else:
            print(f"  -> Failed to open")
            
        if len(cam_readers) >= 2:
            break

    if len(cam_readers) < 2:
        print(f"WARNING: Only found {len(cam_readers)} suitable cameras.")

    # 4. Main Display Loop
    print("\nStarting Main Display Loop. Press 'q' to quit.")
    
    window_name = "Athena Biosignals Dashboard"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 800)
    
    frame_count = 0
    try:
        while True:
            # Layout configuration
            # Top: Cam 1 | Cam 2
            # Bot: Video 1 | Video 2
            
            # --- Prepare Camera Frames ---
            display_cam_frames = []
            for cr in cam_readers:
                f = cr.get_frame()
                if f is None:
                    f = np.zeros((360, 640, 3), dtype=np.uint8)
                    cv2.putText(f, "No Signal", (50, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
                f = cv2.resize(f, (640, 360))
                display_cam_frames.append(f)
            
            while len(display_cam_frames) < 2:
                blank = np.zeros((360, 640, 3), dtype=np.uint8)
                cv2.putText(blank, "Camera Missing", (200, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (100,100,100), 2)
                display_cam_frames.append(blank)
            
            # --- Prepare Video Frames ---
            display_eeg_frames = []
            viz_height = 200
            viz_width = 640
            
            for looper in video_loopers:
                frame = looper.get_frame()
                if frame is not None:
                     frame = cv2.resize(frame, (viz_width, viz_height))
                else:
                     frame = np.zeros((viz_height, viz_width, 3), dtype=np.uint8)
                display_eeg_frames.append(frame)
            
            while len(display_eeg_frames) < 2:
                blank = np.zeros((viz_height, viz_width, 3), dtype=np.uint8)
                cv2.putText(blank, "Video Missing", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (100,100,100), 2)
                display_eeg_frames.append(blank)

            # --- Compose ---
            # Top row: Cam 1 | Cam 2
            top_row = np.hstack(display_cam_frames)
            # Bot row: Video 1 | Video 2
            bot_row = np.hstack(display_eeg_frames)
            
            # Full frame
            full_frame = np.vstack([top_row, bot_row])
            
            cv2.imshow(window_name, full_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("Quit key pressed.")
                break
            
            frame_count += 1
            if frame_count % 300 == 0:
                print(f"Alive... frame {frame_count}")
                
    except KeyboardInterrupt:
        print("KeyboardInterrupt caught.")
    except Exception as e:
        print(f"ERROR: Main loop crashed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Shutting down...")
        for cr in cam_readers:
            cr.stop()
        for looper in video_loopers:
            looper.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
