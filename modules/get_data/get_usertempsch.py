from datetime import datetime, timedelta
from config.db_access import fetch_table


# ======================================================
# HELPER PARSE DATETIME (FIX MDB FORMAT)
# ======================================================
def parse_datetime(value):
    if not value:
        return None

    value = str(value).strip()

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y %H:%M:%S",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except:
            continue

    return None


# ======================================================
# MAIN FUNCTION
# ======================================================
def fetch_user_temp_sch(limit=None, logs=None):
    if logs is None:
        logs = []

    logs.append("Menjalankan sync USER_TEMP_SCH")

    try:
        # 🔥 Ambil semua data dari MDB (stabil)
        rows = fetch_table("USER_TEMP_SCH", logs)

        if not rows:
            logs.append("Data kosong dari MDB")
            return []

        since_date = datetime.now() - timedelta(days=60)
        current_year = datetime.now().year

        filtered = []

        for i, r in enumerate(rows):
            try:
                cometime_raw = r.get("COMETIME")

                if not cometime_raw:
                    continue

                # 🔥 parsing aman
                dt = parse_datetime(cometime_raw)

                if not dt:
                    continue

                # 🔹 filter 2 bulan terakhir
                if dt < since_date:
                    continue

                # 🔹 filter tahun berjalan
                if dt.year != current_year:
                    continue

                filtered.append({
                    "USERID": r.get("USERID"),
                    "SCHCLASSID": r.get("SCHCLASSID"),
                    "COMETIME": dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "LEAVETIME": str(r.get("LEAVETIME")).strip() if r.get("LEAVETIME") else None,
                    "FLAG": r.get("FLAG"),
                })

            except Exception as e:
                logs.append(f"Skip row error: {str(e)}")

        logs.append(f"Total setelah filter: {len(filtered)}")

        # 🔥 BATASI BIAR TIDAK TIMEOUT
        if limit:
            filtered = filtered[:limit]

        return filtered

    except Exception as e:
        logs.append(f"Error fetch_user_temp_sch: {str(e)}")
        return []