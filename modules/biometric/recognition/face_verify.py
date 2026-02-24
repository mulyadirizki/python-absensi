# modules/biometric/face/face_verify.py
from .face_service import FaceService

face_service = FaceService()

def verify_face(image_base64, embedding_saved, threshold=0.65):
    if not image_base64 or embedding_saved is None:
        return {
            "success": False,
            "message": "image_base64 dan embedding_saved wajib"
        }

    emb_new, error = face_service.get_embedding(image_base64)

    if error:
        return {
            "success": False,
            "message": error
        }

    similarity = face_service.cosine_similarity(emb_new, embedding_saved)
    verified = similarity >= threshold

    return {
        "success": True,
        "verified": bool(verified),
        "similarity": similarity,
        "threshold": threshold
    }