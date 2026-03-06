# modules/biometric/face/face_service.py
import base64
import io
import numpy as np
from PIL import Image
from insightface.app import FaceAnalysis

class FaceService:
    def __init__(self):
        # Load model SEKALI saja (critical for performance)
        # self.model = FaceAnalysis(allowed_modules=['detection', 'recognition'])
        # self.model.prepare(ctx_id=-1)  # -1 CPU, 0 GPU
        self.model = FaceAnalysis(
            name="buffalo_s",
            allowed_modules=['detection', 'recognition'],
            providers=['CPUExecutionProvider']
        )

        self.model.prepare(ctx_id=-1, det_size=(640, 640))

    def decode_image(self, base64_str):
        if ',' in base64_str:
            base64_str = base64_str.split(',')[1]

        img_bytes = base64.b64decode(base64_str)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        return np.array(img)

    def detect_face(self, image_base64):
        img = self.decode_image(image_base64)
        faces = self.model.get(img)

        if len(faces) == 0:
            return None, "Tidak ada wajah terdeteksi"

        # Ambil wajah terbesar (lebih akurat untuk login)
        face = max(
            faces,
            key=lambda x: (x.bbox[2]-x.bbox[0]) * (x.bbox[3]-x.bbox[1])
        )

        return face, None

    def get_embedding(self, image_base64):
        face, error = self.detect_face(image_base64)
        if error:
            return None, error

        return face.embedding, None

    def cosine_similarity(self, emb1, emb2):
        emb1 = np.array(emb1, dtype=np.float32)
        emb2 = np.array(emb2, dtype=np.float32)

        return float(
            np.dot(emb1, emb2) /
            (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        )