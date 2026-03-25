# modules/biometric/liveness/liveness_service.py
import insightface
import numpy as np
import cv2
import base64

class LivenessService:
    def __init__(self):
        # deteksi wajah
        self.detector = insightface.model_zoo.get_model('retinaface_r50_v1')
        self.detector.prepare(ctx_id=0, nms=0.4)

        # model liveness
        self.liveness_model = insightface.model_zoo.get_model('antispoof_blazeface')
        self.liveness_model.prepare(ctx_id=0)

    def is_live(self, image_base64):
        try:
            img_data = base64.b64decode(image_base64)
            np_arr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            faces = self.detector.detect(img, threshold=0.5)[0]
            if faces.shape[0] == 0:
                return False, "Wajah tidak terdeteksi"

            x1, y1, x2, y2, _ = faces[0].astype(int)
            face_img = img[y1:y2, x1:x2]

            score = self.liveness_model.predict(face_img)
            return score > 0.5, None
        except Exception as e:
            return False, str(e)