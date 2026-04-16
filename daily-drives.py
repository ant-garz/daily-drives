import os
import sys

from processor.utils import (
    group_clips_by_date,
    sort_clips_by_time,
    summarize_day,
    ensure_output_dirs,
)

from processor.blur import process_clips
from processor.stitch import stitch_clips


VIDEO_EXT = ".mp4"


# -----------------------------
# CLI
# -----------------------------

def choose_date(grouped_clips):
    """Let user pick a date from available clip groups."""
    if not grouped_clips:
        print("No video files found.")
        sys.exit(1)

    dates = sorted(grouped_clips.keys())

    print("\nAvailable dates:")
    for i, date in enumerate(dates, start=1):
        print(f"[{i}] {date} ({len(grouped_clips[date])} clips)")

    while True:
        choice = input("\nSelect a date: ").strip()

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(dates):
                selected_date = dates[idx]
                clips = sort_clips_by_time(grouped_clips[selected_date])
                return selected_date, clips

        print("Invalid selection. Try again.")


def ask_for_blur():
    """Ask user if privacy filtering should be applied."""
    while True:
        choice = input("\nApply privacy blurring? (y/n): ").strip().lower()
        if choice in {"y", "yes"}:
            return True
        if choice in {"n", "no"}:
            return False
        print("Please enter 'y' or 'n'.")


# -----------------------------
# Main pipeline
# -----------------------------

def main():
    print("=== Dashcam Processor ===\n")

    base_path = input("Enter path to dashcam footage: ").strip()

    if not os.path.exists(base_path):
        print("Path does not exist. Is the USB mounted?")
        sys.exit(1)

    print("\nScanning for clips...")
    grouped_clips = group_clips_by_date(base_path)

    date_str, clips = choose_date(grouped_clips)

    start_time, end_time = summarize_day(clips)

    print(f"\nSelected date: {date_str}")
    print(f"Clips: {len(clips)} | Time range: {start_time} -> {end_time}")

    use_blur = ask_for_blur()

    base_output, processed_dir = ensure_output_dirs(date_str, use_blur)

    # -------------------------
    # Step 1: optional processing
    # -------------------------
    if use_blur:
        print("\nRunning privacy processing...")
        final_clips = process_clips(clips, processed_dir)
    else:
        print("\nSkipping privacy processing...")
        final_clips = clips

    # -------------------------
    # Step 2: stitch output
    # -------------------------
    final_output_path = os.path.join(base_output, "final.mp4")

    print("\nStitching clips...")
    stitch_clips(final_clips, final_output_path)

    print(f"\nOutput saved to: {final_output_path}")
    print("Done!")


if __name__ == "__main__":
    main()