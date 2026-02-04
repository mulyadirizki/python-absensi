import sys
import json
import warnings
import pandas as pd
warnings.filterwarnings("ignore", category=UserWarning)

from modules.get_data.get_userinfo import fetch_userinfo
from modules.get_data.get_usertempsch import fetch_user_temp_sch
from modules.get_data.get_schclass import fetch_schclass
from modules.get_data.get_userspeday import fetch_user_speday
from modules.get_data.get_userofrun import fetch_user_of_run
from modules.get_data.get_holidays import fetch_holidays
from modules.get_data.get_from_machine import fetch_attendance_from_machine

def run_userinfo():
    logs = []
    try:
        logs.append("Menjalankan sync USERINFO...")

        df = fetch_userinfo(logs)
        if df is None or df.empty:
            logs.append("Tidak ada data yang berhasil diambil.")
            return {"success": False, "logs": logs}

        logs.append(f"Total data diambil: {len(df)}")
        logs.append("Selesai ambil data user.")

        return {
            "success": True,
            "count": len(df),
            "data": df.to_dict(orient="records"),
            "logs": logs
        }

    except Exception as e:
        logs.append(f"Error: {e}")
        return {"success": False, "logs": logs}

def run_user_temp_sch():
    logs = []
    try:
        logs.append("Menjalankan sync USER_TEMP_SCH")

        df = fetch_user_temp_sch()
        if df is None or df.empty:
            logs.append("Tidak ada data jadwal kerja yang berhasil diambil.")
            return {"success": False, "logs": logs}

        # 🔹 Konversi semua datetime ke string agar bisa di-JSON
        for col in ["COMETIME", "LEAVETIME"]:
            if col in df.columns:
                df[col] = df[col].astype(str)

        logs.append(f"Total jadwal kerja diambil: {len(df)}")

        return {
            "success": True,
            "logs": logs,
            "count": len(df),
            "data": df.to_dict(orient="records")
        }

    except Exception as e:
        logs.append(f"Error: {e}")
        return {"success": False, "logs": logs}

def run_schclass():
    logs = []
    try:
        logs.append("Menjalankan sync SCHCLASS")

        df = fetch_schclass(logs)
        if df is None or df.empty:
            logs.append("Tidak ada data SCHCLASS yang diambil.")
            return {"success": False, "logs": logs}

        # 🔹 Daftar kolom waktu (sesuaikan dengan struktur tabel Access)
        time_cols = ["StartTime", "EndTime", "CheckInTime1", "CheckOutTime1", "CheckInTime2", "CheckOutTime2"]

        # 🔹 Konversi semua kolom
        for col in df.columns:
            if col in time_cols:
                df[col] = df[col].apply(
                    lambda x: x.strftime("%H:%M:%S")
                    if not pd.isna(x) and hasattr(x, "strftime")
                    else None
                )
            else:
                df[col] = df[col].apply(
                    lambda x: int(x) if isinstance(x, float) and x.is_integer()
                    else (str(x) if x is not None else None)
                )

        logs.append(f"Total shift diambil: {len(df)}")
        return {
            "success": True,
            "logs": logs,
            "count": len(df),
            "data": df.to_dict(orient="records"),
        }

    except Exception as e:
        logs.append(f"Error: {e}")
        return {"success": False, "logs": logs}

def run_user_speday():
    logs = []
    try:
        logs.append("Menjalankan sync USER_SPEDAY")

        df = fetch_user_speday()
        if df is None or df.empty:
            logs.append("Tidak ada data jadwal kerja spesial day yang berhasil diambil.")
            return {"success": False, "logs": logs}

        # 🔹 Konversi semua datetime ke string agar bisa di-JSON
        for col in ["STARTSPECDAY", "ENDSPECDAY", "DATE"]:
            if col in df.columns:
                df[col] = df[col].astype(str)

        logs.append(f"Total jadwal kerja spesial day diambil: {len(df)}")

        return {
            "success": True,
            "logs": logs,
            "count": len(df),
            "data": df.to_dict(orient="records")
        }

    except Exception as e:
        logs.append(f"Error: {e}")
        return {"success": False, "logs": logs}

def run_user_of_run():
    logs = []
    try:
        logs.append("Menjalankan sync USER_OF_RUN")

        df = fetch_user_of_run()
        if df is None or df.empty:
            logs.append("Tidak ada data jadwal kerja run of yang berhasil diambil.")
            return {"success": False, "logs": logs}

        # 🔹 Konversi semua datetime ke string agar bisa di-JSON
        for col in ["STARTDATE", "ENDDATE"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], format="%d/%m/%Y", errors="coerce", dayfirst=True).dt.strftime("%Y-%m-%d")

        logs.append(f"Total jadwal kerja of run day diambil: {len(df)}")

        return {
            "success": True,
            "logs": logs,
            "count": len(df),
            "data": df.to_dict(orient="records")
        }

    except Exception as e:
        logs.append(f"Error: {e}")
        return {"success": False, "logs": logs}

def run_holidays():
    logs = []
    try:
        logs.append("Menjalankan sync HOLIDAYS")

        df = fetch_holidays()
        if df is None or df.empty:
            logs.append("Tidak ada data holiday yang berhasil diambil.")
            return {"success": False, "logs": logs}

        # 🔹 Konversi semua datetime ke string agar bisa di-JSON
        for col in ["STARTTIME"]:
            if col in df.columns:
                df[col] = df[col].astype(str)

        logs.append(f"Total holdiays diambil: {len(df)}")

        return {
            "success": True,
            "logs": logs,
            "count": len(df),
            "data": df.to_dict(orient="records")
        }

    except Exception as e:
        logs.append(f"Error: {e}")
        return {"success": False, "logs": logs}

def run_fetch_attendance(ip_list, start_date=None, end_date=None):
    """Ambil log absensi dari 1 atau lebih mesin (bisa multi-IP + filter tanggal)"""
    import pandas as pd
    logs = []
    all_data = []

    from modules.get_data.get_from_machine import fetch_attendance_from_machine

    logs.append(f"Menjalankan sync data absensi dari {len(ip_list)} mesin")

    for ip in ip_list:
        # Kirim parameter start_date & end_date ke mesin
        result = fetch_attendance_from_machine(ip, start_date=start_date, end_date=end_date)

        if result.get("success"):
            # ambil dari key 'logs', bukan 'data'
            count = len(result.get("logs", []))
            all_data.extend(result.get("logs", []))
            logs.append(f"{ip} - {count} log berhasil diambil, SN: {result.get('sn')}")
        else:
            logs.append(f"{ip} - {result.get('message', result.get('error', 'Gagal mengambil data'))}")

    if not all_data:
        logs.append("Tidak ada data absensi yang berhasil diambil.")
        return {"success": False, "logs": logs}

    # ubah ke DataFrame agar konsisten
    df = pd.DataFrame(all_data)
    logs.append(f"Total semua log absensi berhasil diambil: {len(df)}")

    return {
        "success": True,
        "logs": logs,
        "count": len(df),
        "data": df.to_dict(orient="records")
    }



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "logs": ["Argumen tidak ditemukan."]}))
        sys.exit(1)

    command = sys.argv[1]

    if command == "user":
        result = run_userinfo()
        print(json.dumps(result, ensure_ascii=False))
    elif command == "jadwal":
        result = run_user_temp_sch()
        print(json.dumps(result, ensure_ascii=False))
    elif command == "shift":
        result = run_schclass()
        print(json.dumps(result, ensure_ascii=False))
    elif command == "speday":
        result = run_user_speday()
        print(json.dumps(result, ensure_ascii=False))
    elif command == "ofrun":
        result = run_user_of_run()
        print(json.dumps(result, ensure_ascii=False))
    elif command == "holidays":
        result = run_holidays()
        print(json.dumps(result, ensure_ascii=False))
    elif command == "absen":
        import json
        from modules.get_data.get_from_machine import run_fetch_attendance

        if len(sys.argv) < 3:
            print(json.dumps({"success": False, "logs": ["Argumen IP tidak ditemukan."]}, ensure_ascii=False))
            sys.exit(1)

        raw_arg = sys.argv[2]
        try:
            payload = json.loads(raw_arg)
        except json.JSONDecodeError:
            # fallback: replace single quotes
            cleaned = raw_arg.strip().replace("'", '"')
            try: payload = json.loads(cleaned)
            except Exception as e:
                print(json.dumps({"success": False, "logs": [f"JSON payload invalid: {e}"]}, ensure_ascii=False))
                sys.exit(1)

        # ambil IP list dari key "ips" atau field mulai dengan "ip"
        if isinstance(payload, dict):
            ip_list = payload.get("ips") or [v for k, v in payload.items() if k.lower().startswith("ip") and isinstance(v, str)]
            start_date = payload.get("start_date")
            end_date = payload.get("end_date")
        else:
            ip_list = payload
            start_date = None
            end_date = None

        result = run_fetch_attendance(ip_list, start_date=start_date, end_date=end_date)
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(json.dumps({"success": False, "logs": [f"Perintah '{command}' tidak dikenali."]}))
