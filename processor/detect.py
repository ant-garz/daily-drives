import cv2

# Haar cascade face detector
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


def detect_faces(frame, scale=0.7):
    """
    Returns list of bounding boxes: (x, y, w, h)

    Improvements:
    - Downscaled detection for speed
    - Tuned detection parameters for fewer false positives
    - Aspect ratio filtering for noise reduction
    """

    # Resize frame for faster detection (less aggressive than 0.5)
    small_frame = cv2.resize(
        frame,
        (0, 0),
        fx=scale,
        fy=scale
    )

    gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.05,   # finer scan for better accuracy
        minNeighbors=6,     # reduces false positives (trees, poles, etc.)
        minSize=(40, 40),   # ignore very small noise regions
    )

    results = []

    for (x, y, w, h) in faces:

        # Convert back to original frame scale
        x = int(x / scale)
        y = int(y / scale)
        w = int(w / scale)
        h = int(h / scale)

        # ----------------------------
        # Filter 1: aspect ratio check
        # real faces are roughly square
        # ----------------------------
        aspect_ratio = w / float(h)

        if aspect_ratio < 0.75 or aspect_ratio > 1.3:
            continue

        # Keep valid face
        results.append((x, y, w, h))

    return results