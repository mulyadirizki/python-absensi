from datetime import datetime, timedelta
from config.db_access import fetch_table

def parse_date(val):
    if not val:
        return None

    if isinstance(val, datetime):
        return val

    val = str(val).strip()

    # bersihin .0 kalau ada
    if "." in val:
        val = val.split(".")[0]

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",

        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",

        # 🔥 INI YANG PENTING (format kamu)
        "%m/%d/%y %H:%M:%S",
        "%m/%d/%y %H:%M",

        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(val, fmt)
        except:
            continue

    return None

def fetch_user_temp_sch(limit=None, logs=None):
    if logs is None:
        logs = []

    logs.append("Menjalankan sync USER_TEMP_SCH")

    try:
        rows = fetch_table("USER_TEMP_SCH", logs)

        if not rows:
            logs.append("Data kosong dari MDB")
            return []

        logs.append(f"Berhasil ambil {len(rows)} baris dari USER_TEMP_SCH")

        # 🔍 DEBUG sample
        for i, r in enumerate(rows[:5]):
            logs.append(f"Sample COMETIME[{i}]: {r.get('COMETIME')}")

        since_date = datetime.now() - timedelta(days=60)

        filtered = []
        skipped_parse = 0
        skipped_date = 0

        for r in rows:
            try:
                cometime = r.get("COMETIME")
                if not cometime:
                    continue

                dt = parse_date(cometime)
                if not dt:
                    skipped_parse += 1
                    continue

                # ✅ cukup pakai ini saja
                if dt < since_date:
                    skipped_date += 1
                    continue

                filtered.append({
                    "USERID": r.get("USERID"),
                    "SCHCLASSID": r.get("SCHCLASSID"),
                    "COMETIME": dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "LEAVETIME": (
                        str(r.get("LEAVETIME")) if r.get("LEAVETIME") else None
                    ),
                    "FLAG": r.get("FLAG"),
                })

            except Exception as e:
                logs.append(f"Skip row error: {str(e)}")

        logs.append(f"Total setelah filter: {len(filtered)}")
        logs.append(f"Skip parse gagal: {skipped_parse}")
        logs.append(f"Skip tanggal lama: {skipped_date}")

        if limit:
            filtered = filtered[:limit]
            logs.append(f"Limit diterapkan: {limit}")

        return filtered

    except Exception as e:
        logs.append(f"Error fetch_user_temp_sch: {str(e)}")
        return []