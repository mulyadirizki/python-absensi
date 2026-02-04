import requests

def send_karyawan(df, api_url):
    """
    Kirim data USERINFO ke Laravel API
    """
    for _, row in df.iterrows():
        payload = {
            "absensi_user_id": row["USERID"],
            "nama": str(row["Name"]).strip(),
            "pin": str(row["PIN"]) if row["PIN"] else None,
            "departemen": str(row["Departemen"]) if row["Departemen"] else None
        }
        try:
            response = requests.post(api_url, json=payload)
            print(f"USERID {row['USERID']} -> Status {response.status_code}")
        except Exception as e:
            print(f"Error USERID {row['USERID']}: {e}")
