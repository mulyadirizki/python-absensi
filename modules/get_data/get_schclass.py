import pandas as pd
from config.db_access import get_mdb_connection

def fetch_schclass(logs=None):
    if logs is None:
        logs = []

    conn = get_mdb_connection(logs)
    if not conn:
        logs.append("Gagal koneksi ke file MDB.")
        return None

    try:
        # Query ambil semua data shift
        query = """
            SELECT
                schClassid,
                schName,
                StartTime,
                EndTime,
                CheckIn,
                CheckOut,
                CheckInTime1,
                CheckInTime2,
                CheckOutTime1,
                CheckOutTime2,
                WorkDay
            FROM SCHCLASS
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        logs.append(f"Berhasil ambil {len(df)} data dari SCHCLASS.")
        return df

    except Exception as e:
        logs.append(f"Error saat ambil data SCHCLASS: {e}")
        if conn:
            conn.close()
        return None
