import cv2
from insightface.app import FaceAnalysis

# 🔥 PAKAI MODEL RINGAN (WAJIB UNTUK CPU)
app = FaceAnalysis(name="buffalo_s")  # ganti dari buffalo_l
app.prepare(ctx_id=0, det_size=(320, 320))  # kecilkan deteksi = jauh lebih cepat

# Webcam USB (1) + backend stabil
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

# Optimasi performa
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

print("Camera started... Tekan Q untuk keluar")

frame_count = 0
faces = []  # cache hasil deteksi biar UI tidak freeze

while True:
    ret, frame = cap.read()
    if not ret:
        print("Kamera tidak terbaca")
        break

    frame = cv2.flip(frame, 1)

    # Resize supaya ringan (KRUSIAL)
    small_frame = cv2.resize(frame, (320, 240))

    frame_count += 1

    # 🔥 DETEKSI TIAP 3 FRAME (ANTI FREEZE)
    if frame_count % 3 == 0:
        try:
            faces = app.get(small_frame)
        except:
            faces = []

    # Gambar bbox (scale kembali ke ukuran asli)
    scale_x = frame.shape[1] / 320
    scale_y = frame.shape[0] / 240

    for face in faces:
        x1, y1, x2, y2 = face.bbox
        x1 = int(x1 * scale_x)
        y1 = int(y1 * scale_y)
        x2 = int(x2 * scale_x)
        y2 = int(y2 * scale_y)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, "Face Detected",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 255, 0), 2)

    cv2.imshow("Face Recognition - Absensi", frame)

    # WAJIB ada waitKey kecil agar window tidak Not Responding
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
