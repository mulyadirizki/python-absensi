import os
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
    import pyodbc

    def fetch_table(table_name, logs=None):
        if logs is None:
            logs = []

        try:
            mdb_path = get_active_mdb_path()
            logs.append(f"MDB aktif: {mdb_path}")

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

            logs.append(f"Berhasil ambil {len(rows)} baris dari {table_name}")
            return rows

        except Exception as e:
            logs.append(f"Error Windows fetch: {str(e)}")
            return []

else:
    import shutil
    import csv
    from io import StringIO

    def fetch_table(table_name, logs=None):
        if logs is None:
            logs = []

        try:
            mdb_path = get_active_mdb_path()
            logs.append(f"MDB aktif: {mdb_path}")

            if not shutil.which("mdb-export"):
                raise Exception("mdb-export tidak ditemukan (install mdbtools)")

            # jalankan mdb-export
            output = subprocess.check_output(
                ["mdb-export", mdb_path, table_name],
                universal_newlines=True
            )

            if not output.strip():
                logs.append("Tidak ada data")
                return []

            # parsing CSV yang benar
            f = StringIO(output)
            reader = csv.DictReader(f)

            data_rows = []
            for row in reader:
                clean_row = {
                    k: v.strip() if isinstance(v, str) else v
                    for k, v in row.items()
                }
                data_rows.append(clean_row)

            logs.append(f"Berhasil ambil {len(data_rows)} baris dari {table_name}")
            return data_rows

        except Exception as e:
            logs.append(f"Error Linux fetch: {str(e)}")
            return []