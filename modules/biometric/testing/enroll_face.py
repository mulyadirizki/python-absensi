import cv2
import numpy as np
import os
from insightface.app import FaceAnalysis

# Load model ringan (CPU)
app = FaceAnalysis(name="buffalo_s")
app.prepare(ctx_id=0)

def enroll(username):
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    embeddings = []
    print(f"Enrolling wajah untuk: {username}")
    print("Tekan S untuk capture (5x), Q untuk keluar")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        faces = app.get(frame)

        for face in faces:
            x1, y1, x2, y2 = map(int, face.bbox)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)

        cv2.imshow("Enroll Face", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):
            if len(faces) > 0:
                embeddings.append(faces[0].embedding)
                print(f"Captured {len(embeddings)}/10")

        elif key == ord("q"):
            break

        if len(embeddings) >= 10:
            break

    cap.release()
    cv2.destroyAllWindows()

    if len(embeddings) == 0:
        print("Gagal: Tidak ada wajah terdeteksi")
        return

    # Rata-rata embedding (lebih akurat)
    mean_embedding = np.mean(embeddings, axis=0)

    os.makedirs("faces_db", exist_ok=True)
    np.save(f"faces_db/{username}.npy", mean_embedding)

    print(f"Enroll selesai! Disimpan: faces_db/{username}.npy")


if __name__ == "__main__":
    user = input("Masukkan username dokter: ")
    enroll(user)
