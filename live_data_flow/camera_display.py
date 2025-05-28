from __future__ import annotations

import cv2
import logging
import queue
import threading
from typing import Any, Callable
import logging

logger = logging.getLogger(__name__)

def display_video_blocking(source: str, printer: Callable = print) -> None:
    """Open a video source to display it, and block until the user stops it by sending 'q'

    Args:
        source (str): video source to display
        printer (Callable): used to display output message. Defaults to print.
    """
    BufferlessVideoCapture(source, printer)


class BufferlessVideoCapture(threading.Thread):
    """Buffer-less video capture to only display the most recent frame

    Open a video source to display it, and block until the user stops it by sending 'q'

    Args:
        source (str): video source to display
        printer (Callable): used to display output message. Defaults to print.
    """

    def __init__(self, source: str, printer: Callable = print) -> None:
        self.printer = printer
        self.printer("Starting viewer...")
        self.cap = cv2.VideoCapture(source + "?overrun_nonfatal=1&fifo_size=50000000", cv2.CAP_FFMPEG)
        self.q: queue.Queue[Any] = queue.Queue()
        super().__init__(daemon=True)
        self.start()
        self.printer("Viewer started")
        self.printer("Press 'q' in viewer to quit")
        while True:
            try:
                frame = self.q.get()
                im = cv2.resize(frame, (640, 360))
                cv2.imshow("frame", im)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.warning(e)
                break
        self.cap.release()
        cv2.destroyAllWindows()

    def run(self) -> None:
        """Read frames as soon as they are available, keeping only most recent one"""
        while True:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    self.printer("Received empty frame.")
                    continue
                if not self.q.empty():
                    self.q.get_nowait()  # discard previous (unprocessed) frame
                self.q.put(frame)
            except queue.Empty:
                pass
            except:  # pylint: disable=bare-except
                break