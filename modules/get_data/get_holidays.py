import pandas as pd
from config.db_access import get_mdb_connection
from datetime import datetime

def fetch_holidays(limit=None, logs=None):
    if logs is None:
        logs = []

    conn = get_mdb_connection(logs)
    if not conn:
        logs.append("Gagal koneksi ke file MDB.")
        return None

    try:
        # Filter: hanya ambil data dari 3 bulan terakhir tahun berjalan
        query = """
            SELECT HOLIDAYID, HOLIDAYNAME, HOLIDAYYEAR, HOLIDAYMONTH, HOLIDAYDAY, STARTTIME, DURATION, DeptID, HOLIDAYTYPE
            FROM HOLIDAYS
            WHERE Year(STARTTIME) = Year(Date())
        """

        # Kalau mau batasi jumlah user
        if limit:
            query += f" AND HOLIDAYID IN (SELECT TOP {limit} HOLIDAYID FROM HOLIDAYS)"

        df = pd.read_sql_query(query, conn)
        conn.close()

        logs.append(f"Berhasil ambil {len(df)} data HOLIDAYS.")
        return df

    except Exception as e:
        logs.append(f"Error saat ambil data HOLIDAYS: {e}")
        conn.close()
        return None
