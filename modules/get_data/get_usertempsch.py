from datetime import datetime, timedelta
from config.db_access import fetch_table


def fetch_user_temp_sch(limit=None, logs=None):
    if logs is None:
        logs = []

    logs.append("Menjalankan sync USER_TEMP_SCH")

    try:
        # 🔥 ambil semua (pakai mdb-export)
        rows = fetch_table("USER_TEMP_SCH", logs)

        if not rows:
            logs.append("Data kosong dari MDB")
            return []

        # 🔹 filter di Python (lebih stabil dari mdb-sql)
        since_date = datetime.now() - timedelta(days=60)
        current_year = datetime.now().year

        filtered = []

        for r in rows:
            try:
                cometime = r.get("COMETIME")
                if not cometime:
                    continue

                # parse datetime
                try:
                    dt = datetime.fromisoformat(cometime)
                except:
                    continue

                if dt < since_date:
                    continue

                if dt.year != current_year:
                    continue

                filtered.append({
                    "USERID": r.get("USERID"),
                    "SCHCLASSID": r.get("SCHCLASSID"),
                    "COMETIME": str(dt),
                    "LEAVETIME": str(r.get("LEAVETIME")) if r.get("LEAVETIME") else None,
                    "FLAG": r.get("FLAG"),
                })

            except Exception as e:
                logs.append(f"Skip row error: {str(e)}")

        logs.append(f"Total setelah filter: {len(filtered)}")

        # 🔥 batasi biar tidak timeout
        if limit:
            filtered = filtered[:limit]

        return filtered

    except Exception as e:
        logs.append(f"Error fetch_user_temp_sch: {str(e)}")
        return []