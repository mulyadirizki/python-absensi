import pandas as pd
from config.db_access import fetch_table


def fetch_userinfo(logs=None):
    """Ambil semua data USERINFO dari file .mdb"""
    if logs is None:
        logs = []

    rows = fetch_table("USERINFO", logs)

    if not rows:
        logs.append("Data USERINFO kosong atau gagal dibaca.")
        return None

    # Konversi ke DataFrame
    df = pd.DataFrame(rows)

    # Ambil hanya kolom yang dibutuhkan
    cols = ["USERID", "Badgenumber", "Name"]
    df = df[[c for c in cols if c in df.columns]]

    logs.append(f"Berhasil ambil {len(df)} data dari USERINFO.")
    return df
