import cv2
import numpy as np
from insightface.app import FaceAnalysis

# Load model (CPU Friendly + age/gender support)
app = FaceAnalysis(name="buffalo_s")
app.prepare(ctx_id=0)

THRESHOLD = 0.65  # Security level RS

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def load_user_embedding(username):
    try:
        emb = np.load(f"faces_db/{username}.npy")
        return emb
    except:
        return None

def verify(username):
    user_embedding = load_user_embedding(username)

    if user_embedding is None:
        print("User belum enroll wajah!")
        return

    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    print(f"Verifikasi wajah untuk: {username}")
    print("Tekan Q untuk keluar")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Mirror natural (biar tidak kebalik)
        frame = cv2.flip(frame, 1)

        faces = app.get(frame)

        if len(faces) == 0:
            cv2.putText(frame, "No Face Detected", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        else:
            face = faces[0]
            emb = face.embedding
            score = cosine_similarity(emb, user_embedding)

            # Ambil info AI tambahan
            age = int(face.age) if face.age is not None else 0
            gender = "Male" if face.gender == 1 else "Female"

            if score > THRESHOLD:
                status = "VERIFIED"
                color = (0, 255, 0)
                name_label = username
            else:
                status = "NOT MATCH"
                color = (0, 0, 255)
                name_label = "Unknown"

            x1, y1, x2, y2 = map(int, face.bbox)

            # Bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Label utama (Nama + Status)
            label = f"{name_label} | {status}"
            cv2.putText(frame, label, (x1, y1 - 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            # Confidence
            conf_text = f"Conf: {score:.2f}"
            cv2.putText(frame, conf_text, (x1, y1 - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Age & Gender (AI Prediction)
            ag_text = f"Age: {age} | {gender}"
            cv2.putText(frame, ag_text, (x1, y2 + 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        cv2.imshow("RS Face Verification AI (Doctor Access)", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    user = input("Username login: ")
    verify(user)
