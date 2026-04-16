import cv2
import os

from processor.detect import detect_faces

# “How do I transform pixels based on detections?”
def blur_region(frame, x, y, w, h):
    """
    Apply Gaussian blur to region of interest.
    """
    roi = frame[y:y+h, x:x+w]

    if roi.size == 0:
        return frame

    blurred = cv2.GaussianBlur(roi, (51, 51), 30)
    frame[y:y+h, x:x+w] = blurred

    return frame


def apply_privacy_filters(frame, blur_faces=True):
    """
    Runs detection + blur on a single frame.
    """
    if blur_faces:
        faces = detect_faces(frame)
        for (x, y, w, h) in faces:
            frame = blur_region(frame, x, y, w, h)

    return frame


def process_clips(clips, output_dir):
    """
    Reads video files, applies blur frame-by-frame,
    writes processed MP4s.
    """
    processed_paths = []

    total = len(clips)
    print("\nProcessing clips (privacy filter)...")

    for i, clip in enumerate(clips, start=1):
        filename = os.path.basename(clip)
        output_path = os.path.join(
            output_dir,
            filename.replace(".mp4", "_blur.mp4")
        )

        if os.path.exists(output_path):
            print(f"[{i}/{total}] Skipping {filename}")
            processed_paths.append(output_path)
            continue

        print(f"[{i}/{total}] Processing {filename}")

        cap = cv2.VideoCapture(clip)

        if not cap.isOpened():
            print(f"  -> Failed to open {filename}")
            continue

        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = apply_privacy_filters(frame)
            out.write(frame)

        cap.release()
        out.release()

        processed_paths.append(output_path)

    return processed_paths