"""
Insta360 GO 3S Dual Camera Live View

Displays two Insta360 GO 3S cameras side by side in a single window.

Prerequisites:
  1. Both cameras in their Action Pods, connected via USB
  2. Both set to 'Webcam' mode on their touchscreens
  3. pip install opencv-python numpy

Usage:
  python -m live_data_flow.live_insta360
  python -m live_data_flow.live_insta360 0 1     # specify camera indices
"""

import cv2
import numpy as np
import sys
import threading
import queue


class CameraReader(threading.Thread):
    """Reads frames from a camera in a background thread, keeping only the latest."""

    def __init__(self, index: int, backend=cv2.CAP_MSMF):
        super().__init__(daemon=True)
        self.index = index
        self.cap = cv2.VideoCapture(index, backend)
        self.frame_queue: queue.Queue = queue.Queue(maxsize=2)
        self.running = True

        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            # Warmup
            for _ in range(5):
                self.cap.read()

    @property
    def is_ready(self) -> bool:
        return self.cap.isOpened()

    def info(self) -> str:
        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        return f"Index {self.index}: {w}x{h} @ {fps:.0f}fps"

    def run(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret and frame is not None:
                # Drop old frame if queue is full
                if self.frame_queue.full():
                    try:
                        self.frame_queue.get_nowait()
                    except queue.Empty:
                        pass
                self.frame_queue.put(frame)

    def get_frame(self):
        try:
            return self.frame_queue.get(timeout=0.1)
        except queue.Empty:
            return None

    def stop(self):
        self.running = False
        self.cap.release()


def find_cameras(max_index: int = 10) -> list[int]:
    """Find all working camera indices using Media Foundation."""
    found = []
    for idx in range(max_index):
        cap = cv2.VideoCapture(idx, cv2.CAP_MSMF)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None and frame.mean() > 5:
                found.append(idx)
                print(f"  Found camera at index {idx}")
        cap.release()
    return found


def display_dual(indices: list[int]) -> None:
    """Display two cameras side by side."""
    if len(indices) < 2:
        print(f"ERROR: Need 2 cameras, only found {len(indices)}")
        sys.exit(1)

    # Open both cameras
    readers = []
    for i, idx in enumerate(indices[:2]):
        print(f"Opening camera {i+1} at index {idx} ...")
        reader = CameraReader(idx)
        if not reader.is_ready:
            print(f"ERROR: Could not open camera at index {idx}")
            sys.exit(1)
        print(f"  Camera {i+1}: {reader.info()}")
        reader.start()
        readers.append(reader)

    print("\nBoth cameras ready!")
    print("Press 'q' to quit, 'f' to toggle fullscreen")

    window_name = "Insta360 Dual View"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1920, 540)

    fullscreen = False
    display_h = 540  # height to resize each feed to

    while True:
        frames = []
        for reader in readers:
            frame = reader.get_frame()
            if frame is not None:
                # Resize to consistent height, preserving aspect ratio
                h, w = frame.shape[:2]
                scale = display_h / h
                new_w = int(w * scale)
                frame = cv2.resize(frame, (new_w, display_h))
                frames.append(frame)

        if len(frames) == 2:
            # Stack side by side
            combined = np.hstack(frames)
            cv2.imshow(window_name, combined)
        elif len(frames) == 1:
            cv2.imshow(window_name, frames[0])

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("f"):
            fullscreen = not fullscreen
            if fullscreen:
                cv2.setWindowProperty(
                    window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN
                )
            else:
                cv2.setWindowProperty(
                    window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL
                )

    for reader in readers:
        reader.stop()
    cv2.destroyAllWindows()
    print("Cameras closed.")



def main():
    if len(sys.argv) > 2:
        indices = [int(sys.argv[1]), int(sys.argv[2])]
    else:
        print("Auto-detecting cameras (Media Foundation) ...")
        indices = find_cameras()
        if len(indices) < 2:
            print(f"\nERROR: Found {len(indices)} camera(s), need at least 2.")
            print("Make sure both Insta360 cameras are connected and in Webcam mode.")
            sys.exit(1)
        print(f"\nFound {len(indices)} cameras: {indices}")

    display_dual(indices)


if __name__ == "__main__":
    main()
