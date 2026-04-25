import os
from collections import defaultdict
from datetime import datetime
import shutil

VIDEO_EXT = ".mp4"

# “How do I manage file/data organization?”
def group_clips_by_date(base_path: str):
    """
    Scan directory and group videos by modified date.
    """
    grouped = defaultdict(list)

    for root, _, files in os.walk(base_path):
        for file in files:
            if not file.lower().endswith(VIDEO_EXT):
                continue

            full_path = os.path.join(root, file)
            timestamp = os.path.getmtime(full_path)

            date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
            grouped[date_str].append(full_path)

    return grouped


def sort_clips_by_time(clips):
    """Sort clips by modification time."""
    return sorted(clips, key=os.path.getmtime)


def summarize_day(clips):
    """Return start/end time of clip set."""
    times = [os.path.getmtime(c) for c in clips]

    start = datetime.fromtimestamp(min(times)).strftime("%I:%M:%S %p")
    end = datetime.fromtimestamp(max(times)).strftime("%I:%M:%S %p")

    return start, end


def ensure_output_dirs(date_str: str, use_blur: bool):
    """
    output/
        YYYY-MM-DD/
            processed/   (optional)
    """
    base_output = os.path.join("output", date_str)
    os.makedirs(base_output, exist_ok=True)

    processed_dir = None
    if use_blur:
        processed_dir = os.path.join(base_output, "processed")
        os.makedirs(processed_dir, exist_ok=True)

    return base_output, processed_dir

def cleanup_processed_files(processed_dir):
    """
    Deletes the entire processed directory and all temporary files.
    """
    print("Cleaning up temporary files...")

    if processed_dir and os.path.exists(processed_dir):
        try:
            shutil.rmtree(processed_dir)
        except Exception as e:
            print(f"  -> Failed to delete processed directory: {e}")