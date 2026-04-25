# 🤖 AI Smart Locker – Facial Recognition Storage System
ระบบตู้ล็อกเกอร์อัจฉริยะ ปลดล็อกด้วยใบหน้าและรหัส PIN พร้อมระบบจัดการผ่าน Web Application

---

## 📋 ภาพรวมระบบ (System Overview)
AI Smart Locker เป็นระบบบริหารจัดการตู้ล็อกเกอร์ที่เน้นความปลอดภัยและความสะดวกสบายของผู้ใช้งาน โดยนำเทคโนโลยี **Facial Recognition (การจดจำใบหน้า)** มาใช้เป็นกุญแจหลักในการเปิดตู้ ระบบนี้ถูกพัฒนาขึ้นเป็น Web Application เต็มรูปแบบผ่าน **Python (Flask)** โดยใช้ **Microsoft SQL Server** ในการจัดเก็บข้อมูลส่วนบุคคลและประวัติการเข้าใช้งาน

รองรับการจัดการสิทธิ์การเข้าถึงแบบรายบุคคล (License Management) พร้อมแดชบอร์ดสำหรับผู้ดูแลระบบ (Admin) เพื่อดูสถานะตู้แบบ Real-time, บันทึกประวัติการใช้งาน และแจ้งเตือนเมื่อเกิดความผิดปกติ

---

## 🛠️ เทคโนโลยีและเครื่องมือที่ใช้ (Tech Stack & Tools)

| ส่วนของระบบ | เทคโนโลยีและการนำไปใช้งาน |
| :--- | :--- |
| **Back-end Server** | Python 3.10+ และ Flask Framework (จัดการ Routing และ API) |
| **Database** | Microsoft SQL Server (เชื่อมต่อผ่าน `pyodbc` และ ODBC Driver 17) |
| **AI & Computer Vision** | `face_recognition`, `dlib`, `numpy`, `Pillow` (ประมวลผลใบหน้าและแปลงเป็น Feature Vector) |
| **Front-end Design** | HTML5, CSS3 และ CSS Grid/Flexbox สำหรับ Responsive Layout |
| **Interactivity** | Vanilla JavaScript (ระบบกล้อง WebCam, แปลงรูปเป็น Base64, กรองข้อมูลตู้แบบไม่ต้อง Reload) |
| **Development OS** | Windows 10 / 11 |

---

## 📖 คู่มือการใช้งานระบบ (User Manual)

### 1. แดชบอร์ดสำหรับแอดมิน (Admin Dashboard)
* **Real-time Status:** ดูสถานะของตู้ล็อกเกอร์ทั้งหมด (Available 🟢, Occupied 🔴, Offline ⚪) พร้อมระบบจัดกลุ่มตามโซนพื้นที่
* **Emergency Force Release:** แอดมินสามารถสั่ง "บังคับคืนตู้" (Force Release) ได้จากหน้าเว็บในกรณีฉุกเฉิน
* **License Management:** ระบบจัดการสิทธิ์ ว่าผู้ใช้คนไหนสามารถใช้งานล็อกเกอร์ตู้ใดได้บ้าง
* **System Alerts:** แถบการแจ้งเตือนเมื่อมีการสแกนหน้า/PIN ผิดพลาด หรือมีผู้ใช้ส่ง Report แจ้งปัญหา

### 2. ระบบยืนยันตัวตน (Face Authentication)
* **Face Registration:** ผู้ใช้สามารถบันทึกใบหน้าของตนเองผ่านกล้อง WebCam ของอุปกรณ์ เพื่อใช้เป็นกุญแจในการเปิดตู้
* **Dual-Security:** รองรับการปลดล็อกทั้งแบบสแกนใบหน้า (Face Vector Matching) และรหัสผ่าน (PIN Code) 

### 3. ประวัติการใช้งาน (Access Logs)
* ระบบจะบันทึกประวัติทุกครั้งที่มีการเปิด-ปิดตู้ พร้อมระบุวิธีการเข้าถึง (Face, PIN, หรือ Admin-Force) และประทับเวลา (Timestamp) อย่างชัดเจน

---

## 🔑บัญชีสำหรับการทดสอบระบบ (Test Credentials)
สำหรับการเข้าสู่ระบบในการเข้าใช้งานมีดังต่อไปนี้ :
| ระดับผู้เข้าใช้งาน(Role) | ชื่อผู้ใช้ (Username)
| :--- | :--- |
| **Admin (ผู้ดูแลระบบ)** | CPE,SPU,ICT |
| **User (ลูกค้าทั่วไป)** | 6901,6902,6903 |

---

## ⚙️ ขั้นตอนการติดตั้งและตั้งค่าระบบ (Installation Guide)

เพื่อให้ระบบทำงานได้อย่างสมบูรณ์แบบบนระบบปฏิบัติการ Windows กรุณาทำตามขั้นตอนอย่างละเอียดดังนี้:

### 🧰 สิ่งที่ต้องติดตั้งไว้ในเครื่องก่อน (Prerequisites)
1. **Python 3.10+** (ตอนติดตั้งอย่าลืมติ๊ก 'Add Python to PATH')
2. **Microsoft SQL Server** (เวอร์ชัน Express ก็ใช้งานได้) พร้อมด้วยโปรแกรม **SSMS** (SQL Server Management Studio)
3. **ODBC Driver 17 for SQL Server** (จำเป็นสำหรับให้ Python คุยกับฐานข้อมูล)
4. **Visual Studio Build Tools** (เลือก C++ build tools สำหรับการ Compile ไลบรารี `dlib` และ `face_recognition`)
5. **CMake** (เพิ่มเข้า PATH ของ Windows ด้วย)

### 🔗 Step 1: ดาวน์โหลดโปรเจกต์
เปิด Command Prompt หรือ PowerShell แล้วดึงซอร์สโค้ดลงมายังเครื่องของคุณ:
```cmd
git clone https://github.com/ratchasima/Ai_Smart_Locker.git
cd Ai_Smart_Locker
```
---

### 🔗 Step 2: สร้าง Virtual Environment และติดตั้งไลบรารี
เพื่อไม่ให้ไลบรารีของโปรเจกต์นี้ไปรบกวนระบบหลัก แนะนำให้สร้างสภาพแวดล้อมจำลอง (venv):
```cmd
# สร้าง Environment ชื่อ venv
python -m venv venv

# เปิดใช้งาน Environment
venv\Scripts\activate

# ติดตั้งแพ็กเกจทั้งหมดที่จำเป็น
pip install flask pyodbc numpy Pillow werkzeug cmake
pip install dlib
pip install face_recognition
```
### 🔗 Step 3: เตรียมฐานข้อมูล (Database Setup)

1. เปิดโปรแกรม SQL Server Management Studio (SSMS)
2. ล็อกอินเข้าสู่ Server ของคุณด้วย Windows Authentication หรือ SQL Server Authentication
3. สร้างฐานข้อมูลใหม่ชื่อ Smart_Locker
4. เปิดไฟล์สคริปต์สร้างตาราง (ถ้ามี) หรือรันไฟล์ seed_data.py (หลังจากปรับแก้ Connection String ให้ตรงกับเครื่องคุณแล้ว)

---

### 🔗 Step 4: ตั้งค่าการเชื่อมต่อใน Python
เปิดไฟล์ app.py และหาฟังก์ชัน get_db_connection() ตรวจสอบให้แน่ใจว่า Connection String ตรงกับเครื่องของคุณ:
```cmd
def get_db_connection():
    conn = pyodbc.connect(
        r'DRIVER={ODBC Driver 17 for SQL Server};'
        r'SERVER=localhost;' # หรือชื่อ Server ของคุณ
        r'DATABASE=Smart_Locker;'
        r'Trusted_Connection=yes;' # ใช้ yes ถ้าล็อกอินด้วย Windows Auth
    )
    return conn
```
---
### 🔗 Step 5: ทดสอบเปิดเซิร์ฟเวอร์ (Run Local Server)
เมื่อเตรียมทุกอย่างพร้อมแล้ว รันคำสั่งนี้ใน Terminal:
```cmd
python app.py
```
🎉 ยินดีด้วย! ระบบพร้อมใช้งานแล้ว เปิดเบราว์เซอร์ของคุณแล้วไปที่:
```cmd
http://localhost:5000
```
