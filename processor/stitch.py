import os
import subprocess
import tempfile

# “How do I combine videos efficiently?”
def stitch_clips(clips, output_path):
    """
    Stitch videos using FFmpeg concat demuxer.
    Much faster than OpenCV writing.
    """

    if not clips:
        raise ValueError("No clips to stitch")

    # Create temporary file list for FFmpeg
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        list_file = f.name

        for clip in clips:
            # FFmpeg requires this exact format:
            f.write(f"file '{os.path.abspath(clip)}'\n")

    try:
        cmd = [
            "ffmpeg",
            "-y",                     # overwrite output
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-c", "copy",            # NO re-encoding (fast)
            output_path
        ]

        print("\nRunning FFmpeg stitch...")
        subprocess.run(cmd, check=True)

    finally:
        os.remove(list_file)