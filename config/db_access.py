import os
import pyodbc
import subprocess

# ==========================
# KONFIGURASI
# ==========================
network_path = r"\\10.8.8.8\db_absen"  # path network share ......
username = "absen"
password = "absen"
mdb_filename = "DB Okt 2025.mdb" #ghghh

# path lengkap file MDB
MDB_FILE_PATH = os.path.join(network_path, mdb_filename)


# ==========================
# UTILITY FUNGSI
# ==========================
def connect_network_share(path, username, password, logs=None):
    """
    Koneksi ke folder network share menggunakan net use.
    Jika sudah ada koneksi lama ke server yang sama, hapus dulu (menghindari error 1219).
    """
    try:
        # Hapus koneksi lama (jika ada)
        subprocess.run(["net", "use", path, "/delete", "/y"], capture_output=True, text=True)

        # Jalankan koneksi baru
        cmd = ["net", "use", path, f"/user:{username}", password]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            if logs is not None:
                logs.append(f"Terkoneksi ke network share: {path}")
            return True
        else:
            if logs is not None:
                logs.append(f"Gagal konek ke share: {result.stderr.strip()}")
            return False

    except Exception as e:
        if logs is not None:
            logs.append(f"Error saat konek ke share: {e}")
        return False


def disconnect_network_share(path, logs=None):
    """
    Putuskan koneksi dari network share setelah selesai digunakan.
    """
    try:
        subprocess.run(["net", "use", path, "/delete", "/y"], capture_output=True, text=True)
        if logs is not None:
            logs.append(f"Koneksi ke network share {path} diputus.")
    except Exception as e:
        if logs is not None:
            logs.append(f"Gagal disconnect network share: {e}")


def get_mdb_connection(logs=None):
    """
    Membuat koneksi ke database Access (.mdb atau .accdb)
    """
    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        rf"DBQ={MDB_FILE_PATH};"
    )
    try:
        conn = pyodbc.connect(conn_str)
        if logs is not None:
            logs.append(f"Koneksi ke file MDB berhasil: {MDB_FILE_PATH}")
        return conn
    except Exception as e:
        if logs is not None:
            logs.append(f"Gagal koneksi ke file MDB: {e}")
        return None


# ==========================
# FUNGSI UTAMA
# ==========================
def sync_schclass():
    logs = []
    logs.append("Menjalankan sync SCHCLASS")

    # Step 1. Connect ke network share
    if not connect_network_share(network_path, username, password, logs):
        logs.append("Tidak bisa akses folder network share.")
        return {"success": False, "message": "Gagal sinkronisasi data shift.", "logs": logs}

    # Step 2. Koneksi ke file MDB
    conn = get_mdb_connection(logs)
    if not conn:
        logs.append("Gagal koneksi ke file MDB.")
        disconnect_network_share(network_path, logs)
        return {"success": False, "message": "Gagal sinkronisasi data shift.", "logs": logs}

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM SCHCLASS")
        rows = cursor.fetchall()

        logs.append(f"Berhasil ambil {len(rows)} data SCHCLASS dari MDB.")
        # (Contoh: di sini bisa tambahkan proses insert ke DB MySQL / API)
    except Exception as e:
        logs.append(f"Error saat baca tabel SCHCLASS: {e}")
    finally:
        conn.close()
        disconnect_network_share(network_path, logs)

    return {"success": True, "message": "Sinkronisasi SCHCLASS selesai.", "logs": logs}


# ==========================
# JALANKAN LANGSUNG UNTUK TEST
# ==========================
if __name__ == "__main__":
    result = sync_schclass()
    import json
    print(json.dumps(result, indent=4, ensure_ascii=False))
