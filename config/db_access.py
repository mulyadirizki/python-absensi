import os

# ======================================================
# KONFIGURASI
# ======================================================

# Folder hasil mount CIFS (share Windows)
MDB_BASE_PATH = "/mnt/db_absen"

# File penunjuk MDB aktif (ISI: nama file .MDB)
ACTIVE_MDB_FILE = "/mnt/db_absen/active_mdb.txt"


# ======================================================
# HELPER
# ======================================================

def get_active_mdb_path():
    """
    Mengembalikan FULL PATH ke file MDB aktif
    """
    if not os.path.isfile(ACTIVE_MDB_FILE):
        raise FileNotFoundError(
            f"active_mdb.txt tidak ditemukan: {ACTIVE_MDB_FILE}"
        )

    with open(ACTIVE_MDB_FILE, "r", encoding="utf-8") as f:
        mdb_name = f.read().strip()

    if not mdb_name:
        raise ValueError("active_mdb.txt kosong")

    mdb_path = os.path.join(MDB_BASE_PATH, mdb_name)

    if not os.path.isfile(mdb_path):
        raise FileNotFoundError(
            f"File MDB aktif tidak ditemukan: {mdb_path}"
        )

    return mdb_path


def get_active_mdb_name():
    """
    Hanya nama file MDB aktif
    """
    return os.path.basename(get_active_mdb_path())


def list_all_mdb_files():
    """
    List semua file .mdb di folder mount
    """
    if not os.path.isdir(MDB_BASE_PATH):
        return []

    return sorted(
        f for f in os.listdir(MDB_BASE_PATH)
        if f.lower().endswith(".mdb")
    )


# ======================================================
# CLI TEST
# ======================================================
if __name__ == "__main__":
    print("MDB AKTIF :", get_active_mdb_path())
    print("SEMUA MDB :")
    for f in list_all_mdb_files():
        print("-", f)
