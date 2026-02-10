
"""
Convert EEG CSV data to a scrolling video visualization.

Usage:
    python csv_to_video.py input.csv output.mp4 --duration 300 --fps 30

Dependencies:
    pandas, numpy, opencv-python
"""
import argparse
import pandas as pd
import numpy as np
import cv2
import sys

def draw_eeg_frame(buffer, n_channels, width, height):
    """Render the EEG buffer to an image (Opencv)."""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Colors for 4 channels: Green, Blue, Red, Yellow
    colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (0, 255, 255)]
    labels = ["TP9", "AF7", "AF8", "TP10"] # Assumed order
    
    channel_height = height // n_channels
    buffer_len = len(buffer)
    
    for i in range(n_channels):
        if i >= buffer.shape[1]: break
        
        chan_data = buffer[:, i]
        
        # Simple DC offset removal (mean of visible window)
        if len(chan_data) > 0:
            dc_offset = np.mean(chan_data) 
        else:
            dc_offset = 0
        
        # Scale factor (tweak as needed for visibility, maybe auto-scale?)
        # EEG is microvolts. Standard deviation scaling?
        std = np.std(chan_data) if len(chan_data) > 0 else 1.0
        if std == 0: std = 1
        scale = (channel_height / 4) / std  # fit 2 sigma in half height
        
        y_center = int(i * channel_height + channel_height / 2)
        
        points = []
        # Plot every pixel horizontally
        for x in range(width): 
            # Map x to buffer index
            # buffer[0] is oldest, buffer[-1] is newest
            # We want buffer[-1] at x=width, buffer[0] at x=0
            buf_idx = int((x / width) * buffer_len)
            if buf_idx >= len(chan_data): buf_idx = len(chan_data) - 1
            
            val = chan_data[buf_idx] - dc_offset
            y = int(y_center - (val * scale))
            
            # Clamp y
            y_min = i * channel_height
            y_max = (i + 1) * channel_height - 1
            y = max(y_min, min(y_max, y))
            
            points.append((x, y))
        
        # Draw lines
        if len(points) > 1:
            cv2.polylines(img, [np.array(points)], False, colors[i], 1)
        
        # Draw Label
        cv2.putText(img, labels[i], (5, y_center - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, colors[i], 1)
        
        # Draw separator line
        if i < n_channels - 1:
            cv2.line(img, (0, (i+1)*channel_height), (width, (i+1)*channel_height), (50, 50, 50), 1)

    cv2.rectangle(img, (0,0), (width-1, height-1), (100, 100, 100), 1)
    return img

def main():
    parser = argparse.ArgumentParser(description="Convert EEG CSV to Video")
    parser.add_argument("input_csv", help="Path to input CSV file")
    parser.add_argument("output_mp4", help="Path to output MP4 file")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second")
    parser.add_argument("--width", type=int, default=640, help="Video width")
    parser.add_argument("--height", type=int, default=200, help="Video height")
    parser.add_argument("--window", type=float, default=5.0, help="Time window visible (seconds)")
    args = parser.parse_args()

    print(f"Reading CSV: {args.input_csv}")
    try:
        df = pd.read_csv(args.input_csv)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        sys.exit(1)
        
    # Columns expected: timestamps, TP9, AF7, AF8, TP10
    required_cols = ["timestamps", "TP9", "AF7", "AF8", "TP10"]
    if not all(col in df.columns for col in required_cols):
        print(f"Error: CSV must contain columns: {required_cols}")
        print(f"Found: {df.columns}")
        sys.exit(1)

    # Convert timestamps to seconds relative to start
    timestamps = df["timestamps"].values
    t0 = timestamps[0]
    rel_times = timestamps - t0
    
    # Data matrix
    data = df[["TP9", "AF7", "AF8", "TP10"]].values
    n_samples = len(data)
    duration = rel_times[-1]
    
    print(f"Loaded {n_samples} samples spanning {duration:.2f} seconds.")
    
    # Video Writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(args.output_mp4, fourcc, args.fps, (args.width, args.height))
    
    # Sampling simulation
    # We step through time at 1/fps intervals
    video_duration = duration # Render total duration
    total_frames = int(video_duration * args.fps)
    
    print(f"Generating {total_frames} frames...")
    
    for f in range(total_frames):
        current_time = f / args.fps
        
        # Define window [current_time - window_size, current_time]
        start_time = current_time - args.window
        if start_time < 0: start_time = 0
        
        # Find indices
        # Optimization: assume sorted timestamps
        idx_end = np.searchsorted(rel_times, current_time)
        idx_start = np.searchsorted(rel_times, start_time)
        
        # Get chunk
        chunk = data[idx_start:idx_end]
        
        # If chunk is smaller than window (at start), pad with zeros or hold
        # We need exactly 'window' seconds of data roughly. 
        # But for 'draw_eeg_frame', we just pass whatever we have and it stretches it to width.
        # To make it scroll correctly, we should maintain fixed number of samples if possible
        # or map time to x. 
        # For simplicity: draw the chunk. 
        # If chunk is short (at start), it will be stretched. 
        # Better: Pad with zeros at the beginning to fill the window.
        
        # Expected samples in window
        avg_fs = n_samples / duration
        samples_in_window = int(args.window * avg_fs)
        
        buffer = np.zeros((samples_in_window, 4))
        if len(chunk) > 0:
            if len(chunk) >= samples_in_window:
                buffer = chunk[-samples_in_window:]
            else:
                # Fill end of buffer with chunk
                buffer[-len(chunk):] = chunk
                # Beginning remains zeros
        
        frame = draw_eeg_frame(buffer, 4, args.width, args.height)
        out.write(frame)
        
        if f % 100 == 0:
            sys.stdout.write(f"\rFrame {f}/{total_frames}")
            sys.stdout.flush()
            
    out.release()
    print("\nDone! Video saved to:", args.output_mp4)

if __name__ == "__main__":
    main()
