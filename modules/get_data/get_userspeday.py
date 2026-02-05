import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from config.db_access import fetch_table


def fetch_user_speday(limit=None, logs=None):
    if logs is None:
        logs = []

    rows = fetch_table("USER_SPEDAY", logs)

    if not rows:
        logs.append("Data USER_SPEDAY kosong atau gagal dibaca.")
        return None

    df = pd.DataFrame(rows)

    # Pastikan kolom tanggal dikonversi
    date_cols = ["STARTSPECDAY", "ENDSPECDAY", "DATE"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    now = datetime.now()
    three_months_ago = now - relativedelta(months=3)

    # Filter:
    # 1. STARTSPECDAY >= 3 bulan terakhir
    # 2. Tahun STARTSPECDAY = tahun berjalan
    df = df[
        (df["STARTSPECDAY"] >= three_months_ago) &
        (df["STARTSPECDAY"].dt.year == now.year)
    ]

    # Batasi jumlah USERID unik (opsional)
    if limit:
        user_ids = df["USERID"].dropna().unique()[:limit]
        df = df[df["USERID"].isin(user_ids)]

    # Pilih kolom yang dipakai saja
    cols = [
        "USERID",
        "STARTSPECDAY",
        "ENDSPECDAY",
        "DATEID",
        "YUANYING",
        "DATE",
    ]
    df = df[[c for c in cols if c in df.columns]]

    logs.append(f"Berhasil ambil {len(df)} data dari USER_SPEDAY (3 bulan terakhir).")
    return df
