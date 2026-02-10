"""List all available cameras across different backends."""
import cv2

backends = [
    ("DSHOW (DirectShow)", cv2.CAP_DSHOW),
    ("MSMF (Media Foundation)", cv2.CAP_MSMF),
]

for backend_name, backend_id in backends:
    print(f"\n=== {backend_name} ===")
    for idx in range(5):
        cap = cv2.VideoCapture(idx, backend_id)
        if cap.isOpened():
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
            codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
            # Try reading a frame
            ret, frame = cap.read()
            has_frame = "YES" if ret and frame is not None else "NO"
            black = ""
            if ret and frame is not None:
                avg = frame.mean()
                black = f"  avg_brightness={avg:.1f}" + (" (BLACK!)" if avg < 5 else "")
            print(f"  Index {idx}: {w}x{h} @ {fps:.0f}fps  codec={codec}  frame={has_frame}{black}")
            cap.release()
        else:
            cap.release()

print("\nDone.")
