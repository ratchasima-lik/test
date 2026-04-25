import pyodbc
from werkzeug.security import generate_password_hash

def reset_and_seed():
    conn_str = r'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Smart_Locker;Trusted_Connection=yes;'
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    print("--- กำลังล้างข้อมูลเก่า ---")
    cursor.execute("DELETE FROM Access_Logs")
    cursor.execute("DELETE FROM Alerts")
    cursor.execute("DELETE FROM Licenses")
    cursor.execute("DELETE FROM Lockers")
    cursor.execute("DELETE FROM Users")
    conn.commit()

    print("--- กำลังเพิ่มข้อมูลผู้ใช้ (Password: 123456) ---")
    users = [
        (1, 'CPE', 'Admin'),
        (10, 'ICT', 'Admin'),
        (6901, 'SPU', 'User'),
        (6902, 'Sky', 'User'),
        (6903, 'Win', 'User')
    ]
    hashed_pw = generate_password_hash('123456')
    for uid, uname, urole in users:
        cursor.execute("INSERT INTO Users (user_id, username, password, role) VALUES (?, ?, ?, ?)", (uid, uname, hashed_pw, urole))

    print("--- กำลังเพิ่มตู้ล็อกเกอร์ 30 ตู้ ---")
    # ชั้น 1 (101-110) [cite: 42]
    for i in range(101, 111):
        cursor.execute("INSERT INTO Lockers (locker_id, location, status) VALUES (?, ?, ?)", (i, 'Office Floor 1', 'Available'))
    # ชั้น 2 (201-210) [cite: 42]
    for i in range(201, 211):
        cursor.execute("INSERT INTO Lockers (locker_id, location, status) VALUES (?, ?, ?)", (i, 'Lab Floor 2', 'Available'))
    # ชั้น 3 (301-310) [cite: 42]
    for i in range(301, 311):
        cursor.execute("INSERT INTO Lockers (locker_id, location, status) VALUES (?, ?, ?)", (i, 'Workshop Floor 3', 'Available'))

    print("--- มอบสิทธิ์การเข้าใช้งาน (Licenses) ---")
    # CPE (1) & ICT (10) เข้าได้ทุกตู้
    for admin_id in [1, 10]:
        for i in range(101, 311):
            if (101 <= i <= 110) or (201 <= i <= 210) or (301 <= i <= 310):
                cursor.execute("INSERT INTO Licenses (user_id, locker_id) VALUES (?, ?)", (admin_id, i))

    # SPU (6901) เข้าได้เฉพาะชั้น 1 [cite: 43]
    for i in range(101, 111):
        cursor.execute("INSERT INTO Licenses (user_id, locker_id) VALUES (?, ?)", (6901, i))

    # Sky (6902) เข้าได้เฉพาะชั้น 2 [cite: 43]
    for i in range(201, 211):
        cursor.execute("INSERT INTO Licenses (user_id, locker_id) VALUES (?, ?)", (6902, i))

    # Win (6903) เข้าได้เฉพาะชั้น 3 [cite: 43]
    for i in range(301, 311):
        cursor.execute("INSERT INTO Licenses (user_id, locker_id) VALUES (?, ?)", (6903, i))

    conn.commit()
    conn.close()
    print("✅ รีเซ็ตข้อมูลสำเร็จ! แบ่งสิทธิ์ตามชั้นเรียบร้อย")

if __name__ == '__main__':
    reset_and_seed()