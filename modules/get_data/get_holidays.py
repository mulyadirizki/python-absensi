import pandas as pd
from config.db_access import fetch_table
from datetime import datetime


def fetch_holidays(limit=None, logs=None):
    if logs is None:
        logs = []

    rows = fetch_table("HOLIDAYS", logs)

    if not rows:
        logs.append("Data HOLIDAYS kosong atau gagal dibaca.")
        return None

    df = pd.DataFrame(rows)

    # =========================
    # FILTER DI PYTHON (bukan SQL Access)
    # =========================
    current_year = datetime.now().year

    if "STARTTIME" in df.columns:
        df["STARTTIME"] = pd.to_datetime(df["STARTTIME"], errors="coerce")
        df = df[df["STARTTIME"].dt.year == current_year]

    # Batasi jumlah data jika perlu
    if limit:
        df = df.head(limit)

    logs.append(f"Berhasil ambil {len(df)} data HOLIDAYS.")
    return df
