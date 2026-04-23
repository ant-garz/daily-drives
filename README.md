# Dashcam Daily Drives

A command-line tool for organizing and stitching dashcam footage into a single "drive of the day" video. Optionally, the tool can apply a privacy filter that detects and blurs faces in each frame.

## Features
- Automatically scans a directory for dashcam video files
- Groups clips by recording date
- Sorts clips chronologically
- Optionally applies face detection and blur for privacy
- Efficiently stitches clips together using FFmpeg (no re-encoding)

## Project Structure
```text
├── daily-drives.py
└── processor/
    ├── utils.py
    ├── detect.py
    ├── blur.py
    └── stitch.py
```

## Overview
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

## Processing Flow
```text
→ group & sort (utils.py)
→ optional processing (blur.py + detect.py)
→ stitch clips (stitch.py)
→ final output video
```
## Model Setup
This project uses OpenCV's YuNet face detection model.

Download the model file and place it in:

processor/models/

Download link:
https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx

## Audio
Audio is preserved only when privacy filtering is disabled and if it was included in the original video files.

When privacy filtering is enabled, clips are processed using OpenCV, which re-encodes video frames and does not support audio streams. As a result, the final output will not contain audio.

This is a known limitation of the current pipeline design.

## Codec Requirements
This project assumes that all input video clips share the same video and audio codecs, as well as consistent encoding parameters.

The stitching process uses FFmpeg’s concat demuxer with stream copy (`-c copy`), which does not re-encode media. As a result, all clips must be compatible at the container and codec level for successful concatenation.

### Required consistency between clips:
- Same video codec (e.g., H.264)
- Same audio codec (if present)
- Same frame rate
- Same resolution (recommended)
- Same encoding settings

If clips differ in these properties, FFmpeg may fail to stitch them correctly or may drop audio/video streams.

## Examples

### With privacy filtering applied
```
$ python daily-drives.py

=== Dashcam Processor ===

Enter path to dashcam footage: E:\Normal\Front

Scanning for clips...

Available dates:
[1] 2026-04-17 (20 clips)
[2] 2026-04-18 (22 clips)
[3] 2026-04-19 (14 clips)
[4] 2026-04-20 (47 clips)
[5] 2026-04-22 (8 clips)

Select a date (1-5): 5

Selected date: 2026-04-22
Clips: 8 | Time range: 12:05:56 PM -> 02:15:26 PM

Apply privacy blurring? (y/n): y

Running privacy processing...

Processing clips (privacy filter)...
[1/8] Processing clip1.mp4
[2/8] Processing clip2.mp4
...
[8/8] Processing clip8.mp4

Stitching clips...
Cleaning up temporary files...

Output saved to: output/2026-04-22/final.mp4
Done!
Time elapsed: 02:35:43
```

### Without privacy filtering applied
```
$ python daily-drives.py

=== Dashcam Processor ===

Enter path to dashcam footage: E:\Normal\Front

Scanning for clips...

Available dates:
[1] 2026-04-17 (20 clips)
[2] 2026-04-18 (22 clips)
[3] 2026-04-19 (14 clips)
[4] 2026-04-20 (47 clips)
[5] 2026-04-22 (8 clips)

Select a date (1-5): 5

Selected date: 2026-04-22
Clips: 8 | Time range: 12:05:56 PM -> 02:15:26 PM

Apply privacy blurring? (y/n): n

Skipping privacy processing...
Audio will be preserved.

Stitching clips...

Output saved to: output/2026-04-22/final.mp4
Done!
Time elapsed: 00:02:47
```