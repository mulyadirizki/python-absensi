from flask import Flask, request, jsonify
import sys
import os
import json

# Pastikan Python bisa import modules dari folder modules
sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))
sys.path.append(os.path.join(os.path.dirname(__file__), "config"))

from main import (
    run_userinfo,
    run_user_temp_sch,
    run_schclass,
    run_user_speday,
    run_user_of_run,
    run_holidays,
    run_fetch_attendance
)

app = Flask(__name__)

@app.route('/user', methods=['GET'])
def user():
    return jsonify(run_userinfo())

@app.route('/jadwal', methods=['GET'])
def jadwal():
    return jsonify(run_user_temp_sch())

@app.route('/shift', methods=['GET'])
def shift():
    return jsonify(run_schclass())

@app.route('/speday', methods=['GET'])
def speday():
    return jsonify(run_user_speday())

@app.route('/ofrun', methods=['GET'])
def ofrun():
    return jsonify(run_user_of_run())

@app.route('/holidays', methods=['GET'])
def holidays():
    return jsonify(run_holidays())

@app.route('/absen', methods=['POST'])
def absen():
    data = request.get_json()
    ips = data.get('ips', [])
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    result = run_fetch_attendance(ips, start_date=start_date, end_date=end_date)
    return jsonify(result)

if __name__ == "__main__":
    # Jalankan Flask di host 0.0.0.0 agar bisa diakses network
    app.run(host="0.0.0.0", port=5000, debug=True)
