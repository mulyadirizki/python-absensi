import cv2
from insightface.app import FaceAnalysis

# Load model
app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=0)

# Open webcam
cap = cv2.VideoCapture(0)

print("Camera started... Tekan Q untuk keluar")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    faces = app.get(frame)

    for face in faces:
        x1, y1, x2, y2 = map(int, face.bbox)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, "Face Detected", (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

    cv2.imshow("Face Recognition - Local", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
