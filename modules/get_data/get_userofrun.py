import pandas as pd
from datetime import datetime
from config.db_access import fetch_table


def fetch_user_of_run(limit=None, logs=None):
    if logs is None:
        logs = []

    rows = fetch_table("USER_OF_RUN", logs)

    if not rows:
        logs.append("Data USER_OF_RUN kosong atau gagal dibaca.")
        return None

    df = pd.DataFrame(rows)

    # Pastikan kolom tanggal ada
    for col in ["STARTDATE", "ENDDATE"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Filter: tahun berjalan (pengganti Year(STARTDATE) = Year(Date()))
    current_year = datetime.now().year
    df = df[df["STARTDATE"].dt.year == current_year]

    # Batasi jumlah USERID unik (opsional)
    if limit:
        user_ids = df["USERID"].dropna().unique()[:limit]
        df = df[df["USERID"].isin(user_ids)]

    # Pilih kolom yang dipakai saja
    cols = [
        "USERID",
        "NUM_OF_RUN_ID",
        "STARTDATE",
        "ENDDATE",
        "ISNOTOF_RUN",
        "ORDER_RUN",
    ]
    df = df[[c for c in cols if c in df.columns]]

    logs.append(f"Berhasil ambil {len(df)} data dari USER_OF_RUN (tahun berjalan).")
    return df
