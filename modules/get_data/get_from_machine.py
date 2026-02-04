# modules/get_data/get_from_machine.py
import datetime
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from zk import ZK

# 🔹 Cek apakah mesin bisa dihubungi
def is_reachable(ip, port=4370, timeout=2):
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except Exception:
        return False


# 🔹 Parse tanggal dari string ke datetime
def _parse_date(dt_str):
    if not dt_str:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.datetime.strptime(dt_str, fmt)
            # kalau hanya tanggal (tanpa jam), jadikan jam 00:00
            if fmt == "%Y-%m-%d":
                return dt.replace(hour=0, minute=0, second=0)
            return dt
        except Exception:
            continue
    try:
        return datetime.datetime.fromisoformat(dt_str)
    except Exception:
        return None


# 🔹 Ambil log absensi dari 1 mesin
def fetch_attendance_from_machine(ip_address, port=4370, timeout=10, start_date=None, end_date=None):
    zk = ZK(ip_address, port=port, timeout=timeout)
    conn = None
    data = []
    sn = None

    try:
        if not is_reachable(ip_address, port):
            return {"ip": ip_address, "success": False, "count": 0, "error": f"Mesin {ip_address} tidak bisa dihubungi"}

        conn = zk.connect()
        sn = conn.get_serialnumber() if conn else None

        try:
            conn.disable_device()
        except Exception:
            pass

        start_dt = _parse_date(start_date)
        end_dt = _parse_date(end_date)
        if end_dt and end_dt == end_dt.replace(hour=0, minute=0, second=0):
            end_dt = end_dt + datetime.timedelta(days=1)

        # 🔹 Ambil log langsung dari mesin
        attendance = conn.get_attendance() or []

        for att in attendance:
            ts = att.timestamp
            if not isinstance(ts, datetime.datetime):
                try:
                    ts = datetime.datetime.fromisoformat(str(ts))
                except Exception:
                    continue

            # filter log by date range sebelum dikirim ke Laravel
            if start_dt and ts < start_dt:
                continue
            if end_dt and ts >= end_dt:
                continue

            data.append({
                "uid": getattr(att, "uid", None),
                "user_id": str(getattr(att, "user_id", None)),
                "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "status": getattr(att, "status", None),
                "punch": getattr(att, "punch", None),
                "machine_ip": ip_address,
                "serial_number": sn
            })

        return {
            "ip": ip_address,
            "sn": sn,
            "success": True,
            "count": len(data),
            "logs": data
        }

    except Exception as e:
        return {"ip": ip_address, "sn": sn, "success": False, "count": 0, "error": str(e)}

    finally:
        if conn:
            try:
                conn.enable_device()
            except Exception:
                pass
            try:
                conn.disconnect()
            except Exception:
                pass


# 🔹 Multi-thread: ambil banyak mesin sekaligus
def run_fetch_attendance(ip_list, start_date=None, end_date=None, max_workers=5):
    results = []
    total_logs = 0

    with ThreadPoolExecutor(max_workers=min(max_workers, len(ip_list))) as executor:
        futures = {
            executor.submit(fetch_attendance_from_machine, ip, 4370, 10, start_date, end_date): ip
            for ip in ip_list
        }

        for fut in as_completed(futures):
            ip = futures[fut]
            try:
                res = fut.result()
            except Exception as e:
                res = {"ip": ip, "success": False, "count": 0, "error": str(e)}

            results.append(res)
            if res.get("success"):
                total_logs += res.get("count", 0)

    return {
        "success": True,
        "total_machines": len(ip_list),
        "total_logs": total_logs,
        "machines": results
    }
