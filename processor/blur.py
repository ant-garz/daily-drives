import cv2
import os

from processor.detect import detect_faces


# -----------------------------
# Temporal memory settings
# -----------------------------
FACE_MEMORY_FRAMES = 5


def blur_region(frame, x, y, w, h):
    """
    Apply Gaussian blur to region of interest.
    """
    h_img, w_img = frame.shape[:2]

    # clamp bounds (prevents crashes / artifacts)
    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(w_img, x + w)
    y2 = min(h_img, y + h)

    roi = frame[y1:y2, x1:x2]

    if roi.size == 0:
        return frame

    blurred = cv2.GaussianBlur(roi, (51, 51), 30)
    frame[y1:y2, x1:x2] = blurred

    return frame


# -----------------------------
# Stateful tracker (key fix)
# -----------------------------
class FaceMemory:
    def __init__(self, memory_frames=FACE_MEMORY_FRAMES):
        self.memory_frames = memory_frames
        self.last_faces = []
        self.counter = 0

    def update(self, detected_faces):
        if len(detected_faces) > 0:
            self.last_faces = detected_faces
            self.counter = self.memory_frames
        else:
            self.counter -= 1

        if self.counter > 0:
            return self.last_faces
        return []


def apply_privacy_filters(frame, face_memory, blur_faces=True):
    """
    Runs detection + temporal smoothing + blur.
    """
    if not blur_faces:
        return frame

    detected_faces = detect_faces(frame)
    faces_to_use = face_memory.update(detected_faces)

    for (x, y, w, h) in faces_to_use:
        frame = blur_region(frame, x, y, w, h)

    return frame


def process_clips(clips, output_dir):
    """
    Reads video files, applies blur frame-by-frame,
    writes processed MP4s.
    """

    import cv2

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

        # IMPORTANT: per-video memory tracker
        face_memory = FaceMemory()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = apply_privacy_filters(frame, face_memory)
            out.write(frame)

        cap.release()
        out.release()

        processed_paths.append(output_path)

    return processed_paths