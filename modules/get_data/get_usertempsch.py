from datetime import datetime
from config.db_access import fetch_query


def fetch_user_temp_sch(limit=None, logs=None):
    if logs is None:
        logs = []

    logs.append("Menjalankan sync USER_TEMP_SCH")

    query = f"""
    SELECT USERID, SCHCLASSID, COMETIME, LEAVETIME, FLAG
    FROM USER_TEMP_SCH
    WHERE 
        COMETIME IS NOT NULL
        AND COMETIME >= DATE() - 60
    """

    rows = fetch_query(query, logs)

    if not rows:
        logs.append("Data kosong setelah filter")
        return []

    # OPTIONAL LIMIT (biar gak kebanyakan)
    if limit:
        rows = rows[:limit]

    logs.append(f"Final data: {len(rows)} baris")
    return rows