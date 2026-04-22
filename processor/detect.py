import cv2

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


def detect_faces(frame, scale=0.8):
    """
    Returns bounding boxes (x, y, w, h) in original frame coordinates.
    """

    small = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.05,
        minNeighbors=7,
        minSize=(40, 40),
    )

    results = []

    for (x, y, w, h) in faces:

        # scale back to original frame
        x = int(x / scale)
        y = int(y / scale)
        w = int(w / scale)
        h = int(h / scale)

        # light filtering (prevents obvious noise)
        aspect = w / float(h)
        if aspect < 0.75 or aspect > 1.3:
            continue

        results.append((x, y, w, h))

    return results