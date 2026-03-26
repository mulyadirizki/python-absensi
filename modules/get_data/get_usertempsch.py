from datetime import datetime, timedelta
from config.db_access import fetch_query

def fetch_user_temp_sch(limit=None, logs=None):
    if logs is None:
        logs = []

    logs.append("Menjalankan sync USER_TEMP_SCH")

    since_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")

    query = f"""
    SELECT USERID, SCHCLASSID, COMETIME, LEAVETIME, FLAG
    FROM USER_TEMP_SCH
    WHERE 
        COMETIME IS NOT NULL
        AND COMETIME >= '{since_date}'
    """

    logs.append(f"Query: {query}")

    rows = fetch_query(query, logs)

    if not rows:
        logs.append("Data kosong setelah filter")
        return []

    if limit:
        rows = rows[:limit]

    logs.append(f"Final data: {len(rows)} baris")

    return rows