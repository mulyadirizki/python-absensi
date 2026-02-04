import pandas as pd
from config.db_access import get_mdb_connection

def fetch_userinfo(logs=None):
    """Ambil semua data USERINFO dari file .mdb"""
    if logs is None:
        logs = []

    conn = get_mdb_connection(logs)
    if not conn:
        logs.append("Koneksi ke Access gagal.")
        return None

    try:
        query = "SELECT USERID, Badgenumber, [Name] FROM USERINFO"
        df = pd.read_sql_query(query, conn)
        logs.append(f"Berhasil ambil {len(df)} data dari USERINFO.")
        return df
    except Exception as e:
        logs.append(f"Error saat ambil data USERINFO: {e}")
        return None
    finally:
        conn.close()
