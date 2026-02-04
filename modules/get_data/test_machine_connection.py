from zk import ZK, const

zk = ZK('10.16.2.178', port=4370, timeout=30)
try:
    conn = zk.connect()
    print("✅ Connected!")
    users = conn.get_users()
    print(f"Total user: {len(users)}")
    conn.disconnect()
except Exception as e:
    print(f"❌ Error: {e}")
