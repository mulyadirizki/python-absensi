import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from config.db_access import fetch_table


def fetch_user_temp_sch(limit=None, logs=None):
    if logs is None:
        logs = []

    query = """
        SELECT USERID, SCHCLASSID, COMETIME, LEAVETIME, FLAG
        FROM USER_TEMP_SCH
        WHERE 
            COMETIME >= DATEADD(MONTH, -2, GETDATE())
            AND YEAR(COMETIME) = YEAR(GETDATE())
        """
    rows = fetch_table(query, logs, is_query=True)

    if not rows:
        logs.append("Data USER_TEMP_SCH kosong atau gagal dibaca.")
        return None

    df = pd.DataFrame(rows)

    # Pastikan kolom tanggal jadi datetime
    date_cols = ["COMETIME", "LEAVETIME"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    now = datetime.now()
    two_months_ago = now - relativedelta(months=2)

    # Filter:
    # 1. COMETIME >= 2 bulan terakhir
    # 2. Tahun COMETIME = tahun berjalan
    df = df[
        (df["COMETIME"] >= two_months_ago) &
        (df["COMETIME"].dt.year == now.year)
    ]

    # Batasi jumlah USERID unik (opsional)
    if limit:
        user_ids = df["USERID"].dropna().unique()[:limit]
        df = df[df["USERID"].isin(user_ids)]

    # Pilih kolom yang dibutuhkan saja
    cols = [
        "USERID",
        "SCHCLASSID",
        "COMETIME",
        "LEAVETIME",
        "FLAG",
    ]
    df = df[[c for c in cols if c in df.columns]]

    logs.append(f"Berhasil ambil {len(df)} data dari USER_TEMP_SCH (2 bulan terakhir).")
    return df
