import pandas as pd
from config.db_access import fetch_table


def fetch_schclass(logs=None):
    if logs is None:
        logs = []

    rows = fetch_table("SCHCLASS", logs)

    if not rows:
        logs.append("Data SCHCLASS kosong atau gagal dibaca.")
        return None

    # Kalau kamu tetap mau pandas (boleh)
    df = pd.DataFrame(rows)

    logs.append(f"Berhasil ambil {len(df)} data dari SCHCLASS.")
    return df
