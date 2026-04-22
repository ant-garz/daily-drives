# Dashcam Daily Drives

A command-line tool for organizing and stitching dashcam footage into a single "drive of the day" video. Optionally, the tool can apply a privacy filter that detects and blurs faces in each frame.

## Features

- Automatically scans a directory for dashcam video files
- Groups clips by recording date
- Sorts clips chronologically
- Optionally applies face detection and blur for privacy
- Efficiently stitches clips together using FFmpeg (no re-encoding)

## Project Structure
├── daily-drives.py
└── processor/
    ├── utils.py
    ├── detect.py
    ├── blur.py
    └── stitch.py


### Overview

- **daily-drives.py**  
  Entry point for the CLI. Handles user interaction and orchestrates the full processing pipeline.

- **processor/utils.py**  
  Responsible for file discovery, grouping clips by date, sorting them chronologically, and preparing output directories.

- **processor/detect.py**  
  Performs face detection using OpenCV’s Haar cascade model.

- **processor/blur.py**  
  Applies frame-by-frame privacy filtering (face blurring) and writes processed video clips.

- **processor/stitch.py**  
  Combines video clips into a single output file using FFmpeg’s concat demuxer for fast, lossless stitching.

### Processing Flow
→ group & sort (utils.py)
→ optional processing (blur.py + detect.py)
→ stitch clips (stitch.py)
→ final output video