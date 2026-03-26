from datetime import datetime, timedelta
from config.db_access import fetch_query


def fetch_user_temp_sch(limit=None, logs=None):
    if logs is None:
        logs = []

    logs.append("Menjalankan sync USER_TEMP_SCH")

    try:
        # 🔹 2 bulan terakhir (±60 hari)
        since_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")

        query = f"""
        SELECT USERID, SCHCLASSID, COMETIME, LEAVETIME, FLAG
        FROM USER_TEMP_SCH
        WHERE 
            COMETIME IS NOT NULL
            AND COMETIME >= '{since_date}'
        """

        logs.append(f"Query: {query.strip()}")

        rows = fetch_query(query, logs)

        if not rows:
            logs.append("Data kosong setelah filter tanggal")
            return []

        current_year = datetime.now().year

        filtered = []
        user_ids_seen = set()

        for r in rows:
            try:
                cometime = r.get("COMETIME")

                if not cometime:
                    continue

                # 🔹 parsing datetime (handle string dari MDB)
                if isinstance(cometime, str):
                    try:
                        cometime_dt = datetime.fromisoformat(cometime)
                    except:
                        continue
                else:
                    cometime_dt = cometime

                # 🔹 filter tahun berjalan
                if cometime_dt.year != current_year:
                    continue

                # 🔹 limit unique USERID (optional)
                if limit:
                    uid = r.get("USERID")
                    if uid not in user_ids_seen:
                        if len(user_ids_seen) >= limit:
                            continue
                        user_ids_seen.add(uid)

                filtered.append({
                    "USERID": r.get("USERID"),
                    "SCHCLASSID": r.get("SCHCLASSID"),
                    "COMETIME": str(cometime_dt),
                    "LEAVETIME": str(r.get("LEAVETIME")) if r.get("LEAVETIME") else None,
                    "FLAG": r.get("FLAG"),
                })

            except Exception as e:
                logs.append(f"Skip row error: {str(e)}")
                continue

        logs.append(f"Berhasil ambil {len(filtered)} data dari USER_TEMP_SCH (2 bulan terakhir).")

        return filtered

    except Exception as e:
        logs.append(f"Error fetch_user_temp_sch: {str(e)}")
        return []