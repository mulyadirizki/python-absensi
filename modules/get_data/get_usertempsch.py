import pandas as pd
from config.db_access import get_mdb_connection
from datetime import datetime

def fetch_user_temp_sch(limit=None, logs=None):
    if logs is None:
        logs = []

    conn = get_mdb_connection(logs)
    if not conn:
        logs.append("Gagal koneksi ke file MDB.")
        return None

    try:
        # Filter: hanya ambil data dari 2 bulan terakhir tahun berjalan
        query = """
            SELECT USERID, SCHCLASSID, COMETIME, LEAVETIME, FLAG
            FROM USER_TEMP_SCH
            WHERE COMETIME >= DateAdd('m', -2, Date())
              AND Year(COMETIME) = Year(Date())
        """

        # Kalau mau batasi jumlah user
        if limit:
            query += f" AND USERID IN (SELECT TOP {limit} USERID FROM USER_TEMP_SCH)"

        df = pd.read_sql_query(query, conn)
        conn.close()

        logs.append(f"Berhasil ambil {len(df)} data dari USER_TEMP_SCH (3 bulan terakhir).")
        return df

    except Exception as e:
        logs.append(f"Error saat ambil data USER_TEMP_SCH: {e}")
        conn.close()
        return None
