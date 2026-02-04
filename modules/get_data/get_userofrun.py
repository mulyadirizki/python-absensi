import pandas as pd
from config.db_access import get_mdb_connection
from datetime import datetime

def fetch_user_of_run(limit=None, logs=None):
    if logs is None:
        logs = []

    conn = get_mdb_connection(logs)
    if not conn:
        logs.append("Gagal koneksi ke file MDB.")
        return None

    try:
        # Filter: hanya ambil data dari 3 bulan terakhir tahun berjalan
        query = """
            SELECT USERID, NUM_OF_RUN_ID, STARTDATE, ENDDATE, ISNOTOF_RUN, ORDER_RUN
            FROM USER_OF_RUN
            WHERE Year(STARTDATE) = Year(Date())
        """

        # Kalau mau batasi jumlah user
        if limit:
            query += f" AND USERID IN (SELECT TOP {limit} USERID FROM USER_OF_RUN)"

        df = pd.read_sql_query(query, conn)
        conn.close()

        logs.append(f"Berhasil ambil {len(df)} data dari USER_OF_RUN (3 bulan terakhir).")
        return df

    except Exception as e:
        logs.append(f"Error saat ambil data USER_OF_RUN: {e}")
        conn.close()
        return None
