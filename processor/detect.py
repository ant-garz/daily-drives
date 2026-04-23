import cv2
import os


# -----------------------------
# Model configuration
# -----------------------------

# Build path to the ONNX model relative to this file
MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "models",
    "face_detection_yunet_2023mar.onnx"
)

# Validate that model exists (fail early with clear message)
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"YuNet model not found at: {MODEL_PATH}\n"
    )


# -----------------------------
# Initialize detector
# -----------------------------

# Create the YuNet face detector
# This is done once and reused for all frames (important for performance)
face_detector = cv2.FaceDetectorYN.create(
    MODEL_PATH,
    "",                  # no config file needed
    (320, 320),          # default input size (will be updated dynamically)
    score_threshold=0.6, # confidence threshold (higher = fewer false positives)
    nms_threshold=0.3,   # non-max suppression threshold
    top_k=5000           # max number of detections
)


# -----------------------------
# Face detection function
# -----------------------------

def detect_faces(frame):
    """
    Detect faces using OpenCV's YuNet DNN model.

    Returns:
        List of bounding boxes in format: (x, y, w, h)
    """

    # -----------------------------
    # 1. Get frame dimensions
    # -----------------------------
    # YuNet requires knowing the input size per frame
    height, width = frame.shape[:2]

    # -----------------------------
    # 2. Set detector input size
    # -----------------------------
    # Must match the current frame size
    face_detector.setInputSize((width, height))

    # -----------------------------
    # 3. Run detection
    # -----------------------------
    # Returns:
    #   - retval (unused)
    #   - detections (Nx15 array or None)
    _, detections = face_detector.detect(frame)

    results = []

    # -----------------------------
    # 4. Process detections
    # -----------------------------
    if detections is not None:
        for det in detections:
            # Each detection contains:
            # [x, y, w, h, score, landmarks...]

            x, y, w_box, h_box = det[:4]

            # Convert to integers (pixel coordinates)
            x = int(x)
            y = int(y)
            w_box = int(w_box)
            h_box = int(h_box)

            # -----------------------------
            # 5. Optional filtering
            # -----------------------------
            # Skip extremely small detections (noise)
            if w_box < 30 or h_box < 30:
                continue

            results.append((x, y, w_box, h_box))

    # -----------------------------
    # 6. Return final bounding boxes
    # -----------------------------
    return results