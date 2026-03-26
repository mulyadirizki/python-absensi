from xml.parsers.expat import model

from flask import Flask, request, jsonify
import sys
import os
import json
import logging

# -----------------------------
# Setup paths untuk import modules
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "modules"))
sys.path.append(os.path.join(BASE_DIR, "config"))

from main import (
    run_userinfo,
    run_user_temp_sch,
    run_schclass,
    run_user_speday,
    run_user_of_run,
    run_holidays,
    run_fetch_attendance
)

from biometric.recognition.face_register import register_face_multi
from biometric.recognition.face_verify import verify_face

# -----------------------------
# Flask app
# -----------------------------
app = Flask(__name__)

# -----------------------------
# Setup logging production
# -----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------
# Routes
# -----------------------------
@app.route('/user', methods=['GET', 'POST'])
def user():
    try:
        return jsonify(run_userinfo())
    except Exception as e:
        logger.exception("Error in /user")
        return jsonify({"error": str(e)}), 500

@app.route('/jadwal', methods=['GET', 'POST'])
def jadwal():
    try:
        return jsonify(run_user_temp_sch())
    except Exception as e:
        logger.exception("Error in /jadwal")
        return jsonify({"error": str(e)}), 500

@app.route('/shift', methods=['GET', 'POST'])
def shift():
    try:
        return jsonify(run_schclass())
    except Exception as e:
        logger.exception("Error in /shift")
        return jsonify({"error": str(e)}), 500

@app.route('/speday', methods=['GET', 'POST'])
def speday():
    try:
        return jsonify(run_user_speday())
    except Exception as e:
        logger.exception("Error in /speday")
        return jsonify({"error": str(e)}), 500

@app.route('/ofrun', methods=['GET', 'POST'])
def ofrun():
    try:
        return jsonify(run_user_of_run())
    except Exception as e:
        logger.exception("Error in /ofrun")
        return jsonify({"error": str(e)}), 500

@app.route('/holidays', methods=['GET', 'POST'])
def holidays():
    try:
        return jsonify(run_holidays())
    except Exception as e:
        logger.exception("Error in /holidays")
        return jsonify({"error": str(e)}), 500

@app.route('/absen', methods=['POST'])
def absen():
    try:
        data = request.get_json()
        ips = data.get('ips', [])
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        result = run_fetch_attendance(ips, start_date=start_date, end_date=end_date)
        return jsonify(result)
    except Exception as e:
        logger.exception("Error in /absen")
        return jsonify({"error": str(e)}), 500

@app.route("/api/hello", methods=["GET"])
def hello():
    return jsonify({"message": "Hello from Python API"})

# =========================
# FACE REGISTER (Dipanggil Laravel saat daftar wajah)
# =========================
@app.route("/face/register", methods=["POST"])
def face_register_api():
    try:
        data = request.get_json(force=True)

        user_id = data.get("user_id")
        images_base64 = data.get("images_base64")  # ⬅️ sekarang array

        result = register_face_multi(user_id, images_base64)
        return jsonify(result)

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# =========================
# FACE VERIFY (LOGIN DOKTER 1:1)
# =========================
@app.route("/face/verify", methods=["POST"])
def face_verify_api():
    try:
        data = request.get_json(force=True)

        image_base64 = data.get("image_base64")
        embedding_saved = data.get("embedding_saved")
        threshold = float(data.get("threshold", 0.65))

        result = verify_face(image_base64, embedding_saved, threshold)
        return jsonify(result)

    except Exception as e:
        logger.exception("Error in /face/verify")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "Face Recognition AI (InsightFace)"
    })

# -----------------------------
# Jangan pakai debug mode di production
# -----------------------------
if __name__ == "__main__":
    # Hanya untuk testing local, bukan production
    app.run(host="0.0.0.0", port=5000)
