import os
import sys
import subprocess
import platform

# ======================================================
# KONFIGURASI
# ======================================================
MDB_BASE_PATH = "/mnt/db_absen"
ACTIVE_MDB_FILE = os.path.join(MDB_BASE_PATH, "active_mdb.txt")


# ======================================================
# HELPER
# ======================================================
def get_active_mdb_path():
    if not os.path.isfile(ACTIVE_MDB_FILE):
        raise FileNotFoundError(f"active_mdb.txt tidak ditemukan: {ACTIVE_MDB_FILE}")
    with open(ACTIVE_MDB_FILE, "r", encoding="utf-8") as f:
        mdb_name = f.read().strip()
    if not mdb_name:
        raise ValueError("active_mdb.txt kosong")
    mdb_path = os.path.join(MDB_BASE_PATH, mdb_name)
    if not os.path.isfile(mdb_path):
        raise FileNotFoundError(f"File MDB aktif tidak ditemukan: {mdb_path}")
    return mdb_path


def get_active_mdb_name():
    return os.path.basename(get_active_mdb_path())


def list_all_mdb_files():
    if not os.path.isdir(MDB_BASE_PATH):
        return []
    return sorted(f for f in os.listdir(MDB_BASE_PATH) if f.lower().endswith(".mdb"))


# ======================================================
# GET TABLE DATA (multi-platform)
# ======================================================
if platform.system() == "Windows":
    # Windows → pakai pyodbc
    import pyodbc

    def fetch_table(table_name):
        mdb_path = get_active_mdb_path()
        conn_str = (
            r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
            f"DBQ={mdb_path};"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        cols = [column[0] for column in cursor.description]
        rows = [dict(zip(cols, row)) for row in cursor.fetchall()]
        conn.close()
        return rows

else:
    # Linux → pakai mdbtools
    import shutil

    def fetch_table(table_name):
        mdb_path = get_active_mdb_path()
        if not shutil.which("mdb-export"):
            raise EnvironmentError("mdb-export tidak ditemukan, install mdbtools!")
        try:
            output = subprocess.check_output(
                ["mdb-export", mdb_path, table_name], universal_newlines=True
            )
            lines = output.strip().splitlines()
            if not lines:
                return []
            header = lines[0].split(",")
            data_rows = []
            for line in lines[1:]:
                values = line.split(",")
                row = {header[i]: values[i] for i in range(len(header))}
                data_rows.append(row)
            return data_rows
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error membaca tabel {table_name}: {str(e)}")