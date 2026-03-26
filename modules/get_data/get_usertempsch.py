from datetime import datetime, timedelta
from config.db_access import fetch_query

def fetch_user_temp_sch(limit=None, logs=None):
    if logs is None:
        logs = []

    logs.append("Menjalankan sync USER_TEMP_SCH")

    try:
        # 🔹 Hitung tanggal (60 hari ke belakang)
        since_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")

        # 🔹 Gunakan format aman untuk MDB (string date)
        query = f"""
        SELECT USERID, SCHCLASSID, COMETIME, LEAVETIME, FLAG
        FROM USER_TEMP_SCH
        WHERE 
            COMETIME IS NOT NULL
            AND COMETIME >= '{since_date}'
        """

        logs.append(f"Query: {query.strip()}")

        rows = fetch_query(query, logs)

        # 🔹 Validasi hasil
        if not isinstance(rows, list):
            logs.append("ERROR: hasil query bukan list")
            return []

        if not rows:
            logs.append("Data kosong setelah filter")
            return []

        # 🔹 Optional limit
        if limit and isinstance(limit, int):
            rows = rows[:limit]

        # 🔹 Normalisasi data (penting!)
        cleaned_rows = []
        for r in rows:
            cleaned_rows.append({
                "USERID": r.get("USERID"),
                "SCHCLASSID": r.get("SCHCLASSID"),
                "COMETIME": r.get("COMETIME"),
                "LEAVETIME": r.get("LEAVETIME"),
                "FLAG": r.get("FLAG"),
            })

        logs.append(f"Final data: {len(cleaned_rows)} baris")

        return cleaned_rows

    except Exception as e:
        logs.append(f"Error fetch_user_temp_sch: {str(e)}")
        return []