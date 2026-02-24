# modules/biometric/face/face_register.py
import numpy as np
from .face_service import FaceService

face_service = FaceService()

def register_face_multi(user_id, images_base64):
    """
    images_base64: list of base64 images (3-5 frame)
    """
    if not user_id:
        return {
            "success": False,
            "message": "user_id wajib"
        }

    if not images_base64 or not isinstance(images_base64, list):
        return {
            "success": False,
            "message": "images_base64 harus array 3-5 frame"
        }

    embeddings = []
    failed_frames = 0

    for idx, image_base64 in enumerate(images_base64):
        emb, error = face_service.get_embedding(image_base64)

        if error:
            failed_frames += 1
            continue

        embeddings.append(emb)

    if len(embeddings) == 0:
        return {
            "success": False,
            "message": "Tidak ada wajah valid terdeteksi di semua frame"
        }

    # 🔥 CORE: Average embedding (ANTI SPOOF & STABIL)
    final_embedding = np.mean(embeddings, axis=0)

    return {
        "success": True,
        "message": f"Registrasi wajah berhasil ({len(embeddings)} frame valid, {failed_frames} gagal)",
        "embedding": final_embedding.tolist(),
        "frames_used": len(embeddings)
    }