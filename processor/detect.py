import cv2

# Face detector (built-in OpenCV model)
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# “Where are the faces in this frame?”
def detect_faces(frame):
    """
    Returns list of bounding boxes: (x, y, w, h)
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
    )

    return faces