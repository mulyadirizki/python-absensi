import subprocess
import csv
from io import StringIO

# ==========================
# KONFIGURASI
# ==========================
MDB_FILE_PATH = "/mnt/db_absen/DB Nov 2025_update.MDB"


def fetch_table(table_name, logs=None):
    """
    Ambil data dari tabel MDB menggunakan mdb-export
    Return: list of dict
    """
    try:
        cmd = ["mdb-export", MDB_FILE_PATH, table_name]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(result.stderr)

        reader = csv.DictReader(StringIO(result.stdout))
        rows = list(reader)

        if logs is not None:
            logs.append(f"Berhasil ambil {len(rows)} row dari tabel {table_name}")

        return rows

    except Exception as e:
        if logs is not None:
            logs.append(f"Gagal baca tabel {table_name}: {e}")
        return []
