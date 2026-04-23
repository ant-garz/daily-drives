import os
import subprocess
import tempfile

# “How do I combine videos efficiently?”
def stitch_clips(clips, output_path):
    """
    Stitch videos using FFmpeg concat demuxer (silent mode).

    - No console spam from FFmpeg
    - Raises error if stitching fails
    - Uses stream copy for speed (no re-encoding)
    """

    if not clips:
        raise ValueError("No clips to stitch")

    # -----------------------------
    # 1. Create temporary file list for FFmpeg
    # -----------------------------
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        list_file = f.name

        for clip in clips:
            f.write(f"file '{os.path.abspath(clip)}'\n")

    try:
        # -----------------------------
        # 2. FFmpeg concat command
        # -----------------------------
        cmd = [
            "ffmpeg",
            "-y",              # overwrite output
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,

            # -----------------------------
            # 3. Silent + clean logging
            # -----------------------------
            "-hide_banner",
            "-loglevel", "error",

            # -----------------------------
            # 4. Fast stream copy (no re-encode)
            # -----------------------------
            "-c", "copy",

            output_path
        ]

        print("\nStitching clips...")

        # -----------------------------
        # 5. Fully silent execution
        # -----------------------------
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    finally:
        # -----------------------------
        # 6. Cleanup temp file list
        # -----------------------------
        os.remove(list_file)