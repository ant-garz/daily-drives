import cv2
import os

from processor.detect import detect_faces


# -----------------------------
# Settings
# -----------------------------
FACE_MEMORY_FRAMES = 10      # how long to persist faces
SMOOTHING_ALPHA = 0.6        # 0 = no smoothing, 1 = no memory
PADDING_RATIO = 0.3          # expand bounding boxes
BLUR_KERNEL = (71, 71)       # stronger blur
BLUR_SIGMA = 50


# -----------------------------
# Helpers
# -----------------------------
def expand_box(x, y, w, h):
    pad_w = int(w * PADDING_RATIO)
    pad_h = int(h * PADDING_RATIO)

    return (
        x - pad_w,
        y - pad_h,
        w + 2 * pad_w,
        h + 2 * pad_h
    )


def smooth_boxes(old_boxes, new_boxes):
    """
    Smooth bounding boxes between frames.
    Assumes small number of faces (dashcam use case).
    """
    if not old_boxes:
        return new_boxes

    smoothed = []

    for i, (nx, ny, nw, nh) in enumerate(new_boxes):
        if i < len(old_boxes):
            ox, oy, ow, oh = old_boxes[i]

            x = int(SMOOTHING_ALPHA * nx + (1 - SMOOTHING_ALPHA) * ox)
            y = int(SMOOTHING_ALPHA * ny + (1 - SMOOTHING_ALPHA) * oy)
            w = int(SMOOTHING_ALPHA * nw + (1 - SMOOTHING_ALPHA) * ow)
            h = int(SMOOTHING_ALPHA * nh + (1 - SMOOTHING_ALPHA) * oh)
        else:
            x, y, w, h = nx, ny, nw, nh

        smoothed.append((x, y, w, h))

    return smoothed


def blur_region(frame, x, y, w, h):
    """
    Apply Gaussian blur safely within frame bounds.
    """
    h_img, w_img = frame.shape[:2]

    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(w_img, x + w)
    y2 = min(h_img, y + h)

    roi = frame[y1:y2, x1:x2]

    if roi.size == 0:
        return frame

    blurred = cv2.GaussianBlur(roi, BLUR_KERNEL, BLUR_SIGMA)
    frame[y1:y2, x1:x2] = blurred

    return frame


# -----------------------------
# Temporal memory
# -----------------------------
class FaceMemory:
    def __init__(self, memory_frames=FACE_MEMORY_FRAMES):
        self.memory_frames = memory_frames
        self.last_faces = []
        self.counter = 0

    def update(self, detected_faces):
        if len(detected_faces) > 0:
            # Expand boxes first
            expanded = [expand_box(*f) for f in detected_faces]

            # Smooth with previous
            smoothed = smooth_boxes(self.last_faces, expanded)

            self.last_faces = smoothed
            self.counter = self.memory_frames
        else:
            self.counter -= 1

        if self.counter > 0:
            return self.last_faces

        return []


# -----------------------------
# Frame processing
# -----------------------------
def apply_privacy_filters(frame, face_memory, blur_faces=True):
    if not blur_faces:
        return frame

    detected_faces = detect_faces(frame)
    faces_to_blur = face_memory.update(detected_faces)

    for (x, y, w, h) in faces_to_blur:
        frame = blur_region(frame, x, y, w, h)

    return frame


# -----------------------------
# Main clip processor
# -----------------------------
def process_clips(clips, output_dir):
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

        # Create memory tracker per clip
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