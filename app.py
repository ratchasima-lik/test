from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import pyodbc
from datetime import datetime
import os
import base64
import json
import numpy as np
from PIL import Image
import io
import face_recognition 

app = Flask(__name__)
app.secret_key = 'ai_smart_locker_secret'
os.makedirs('static/faces', exist_ok=True)

def get_db_connection():
    conn = pyodbc.connect(r'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Smart_Locker;Trusted_Connection=yes;')
    conn.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
    conn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
    conn.setencoding(encoding='utf-8')
    return conn

def init_db_updates():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        try: cursor.execute("SELECT log_status FROM Access_Logs")
        except:
            cursor.execute("ALTER TABLE Access_Logs ADD log_status VARCHAR(10) DEFAULT 'Unread'")
            cursor.execute("UPDATE Access_Logs SET log_status = 'Unread' WHERE log_status IS NULL")
            conn.commit()
        conn.close()
    except: pass
init_db_updates()

def process_incoming_face(base64_string):
    try:
        base64_string = base64_string.replace(' ', '+')
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        img_data = base64.b64decode(base64_string)
        img = Image.open(io.BytesIO(img_data)).convert('RGB')
        img_np = np.array(img, dtype=np.uint8)
        encodings = face_recognition.face_encodings(img_np)
        return encodings, img
    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}") 
        return None, None

@app.route('/')
def index():
    if 'logged_in' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT ref_image_path FROM Users WHERE user_id = ?", (session['user_id'],))
    user_row = cursor.fetchone()
    profile_img = user_row[0] if user_row and user_row[0] else None
    
    if session['role'] == 'Admin':
        cursor.execute("SELECT L.locker_id, L.location, L.status, (SELECT TOP 1 U.username FROM Access_Logs A JOIN Users U ON A.user_id = U.user_id WHERE A.locker_id = L.locker_id ORDER BY A.access_time DESC) as [current_user] FROM Lockers L ORDER BY L.locker_id")
    else:
        cursor.execute("SELECT L.locker_id, L.location, L.status, '' as [current_user] FROM Lockers L JOIN Licenses Li ON L.locker_id = Li.locker_id WHERE Li.user_id = ? ORDER BY L.locker_id", (session['user_id'],))
    lockers_data = cursor.fetchall()

    alerts = []
    unread_count = 0

    if session['role'] == 'Admin':
        cursor.execute("SELECT alert_id, alert_type as title, alert_time as time, intruder_image as detail FROM Alerts ORDER BY alert_time DESC")
        for row in cursor.fetchall(): alerts.append({'title': row.title, 'time': row.time.strftime('%Y-%m-%d %H:%M'), 'detail': row.detail})
        cursor.execute("SELECT COUNT(*) FROM Alerts WHERE alert_status = 'Pending'")
        unread_count = cursor.fetchone()[0]
    else:
        cursor.execute("SELECT log_id, 'เข้าใช้งานตู้ ' + CAST(locker_id AS VARCHAR) as title, access_time as time, 'วิธี: ' + access_method as detail FROM Access_Logs WHERE user_id = ? ORDER BY access_time DESC", (session['user_id'],))
        for row in cursor.fetchall(): alerts.append({'title': row.title, 'time': row.time.strftime('%Y-%m-%d %H:%M'), 'detail': row.detail})
        try:
            cursor.execute("SELECT COUNT(*) FROM Access_Logs WHERE user_id = ? AND log_status = 'Unread'", (session['user_id'],))
            unread_count = cursor.fetchone()[0]
        except: unread_count = 0
    
    conn.close()
    
    # เพิ่มส่วนคำนวณจำนวนตู้และการจัดกลุ่ม
    status_counts = {'Available': 0, 'Occupied': 0, 'Offline': 0}
    grouped_lockers = {}
    
    for row in lockers_data:
        # นับจำนวนสถานะ
        if row.status in status_counts:
            status_counts[row.status] += 1
            
        # จัดกลุ่มตาม Location
        if row.location not in grouped_lockers: 
            grouped_lockers[row.location] = []
        grouped_lockers[row.location].append(row)

    return render_template('index.html', 
                           username=session['username'], 
                           role=session['role'], 
                           user_id=session['user_id'], 
                           grouped_lockers=grouped_lockers, 
                           alerts=alerts, 
                           unread_count=unread_count, 
                           profile_img=profile_img,
                           status_counts=status_counts) # ส่งตัวแปรนี้เพิ่มเข้าไป

@app.route('/read_alerts', methods=['POST'])
def read_alerts():
    conn = get_db_connection()
    cursor = conn.cursor()
    if session.get('role') == 'Admin': cursor.execute("UPDATE Alerts SET alert_status = 'Read' WHERE alert_status = 'Pending'")
    else:
        try: cursor.execute("UPDATE Access_Logs SET log_status = 'Read' WHERE user_id = ? AND log_status = 'Unread'", (session['user_id'],))
        except: pass
    conn.commit(); conn.close()
    return jsonify({"status": "success"})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_id, password = request.form['login_id'], request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, username, password, role FROM Users WHERE CAST(user_id AS VARCHAR) = ? OR username = ?", (login_id, login_id))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user.password, password):
            session.update({'logged_in': True, 'user_id': user.user_id, 'username': user.username, 'role': user.role})
            return redirect(url_for('index'))
        return render_template('login.html', error="ชื่อหรือรหัสผ่านไม่ถูกต้อง")
    return render_template('login.html')

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))

@app.route('/face_auth', methods=['GET', 'POST'])
def face_auth():
    if request.method == 'POST':
        password = request.form['password']
        image_data = request.form.get('image_data', '')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM Users WHERE user_id = ?", (session['user_id'],))
        user_row = cursor.fetchone()
        
        if user_row and check_password_hash(user_row[0], password):
            try:
                encodings, clean_img = process_incoming_face(image_data)
                
                if encodings and len(encodings) > 0:
                    face_vector = encodings[0].tolist()
                    vector_json = json.dumps(face_vector)
                    
                    filepath = f"static/faces/user_{session['user_id']}.jpg"
                    clean_img.save(filepath, format="JPEG")
                    
                    cursor.execute("UPDATE Users SET ref_image_path = ?, feature_vector = ? WHERE user_id = ?", (f"/{filepath}", vector_json, session['user_id']))
                    conn.commit()
                    flash("🤖 AI ประมวลผลและบันทึกใบหน้าของคุณสำเร็จ!", "success")
                else:
                    flash("❌ AI ตรวจไม่พบใบหน้า กรุณาให้หน้าอยู่ในกล้องชัดๆ!", "error")
            except Exception as e:
                flash(f"เกิดข้อผิดพลาด: {str(e)}", "error")
        else:
            flash("รหัสผ่านไม่ถูกต้อง!", "error")
            
        conn.close()
        return redirect(url_for('index'))
        
    return render_template('face_auth.html')

@app.route('/api/locker_action', methods=['POST'])
def api_locker_action():
    data = request.json
    locker_id, pin, action, method = data.get('locker_id'), data.get('pin'), data.get('action'), data.get('method')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT status FROM Lockers WHERE locker_id = ?", (locker_id,))
    current_status = cursor.fetchone()[0]
    log_id = int(datetime.now().timestamp() % 1000000)

    target_user_id = session['user_id']
    if current_status == 'Occupied':
        cursor.execute("SELECT TOP 1 U.user_id, U.password, U.feature_vector FROM Access_Logs A JOIN Users U ON A.user_id = U.user_id WHERE A.locker_id = ? AND A.access_method NOT LIKE '%Return%' ORDER BY A.access_time DESC", (locker_id,))
        occupant = cursor.fetchone()
        if not occupant: return jsonify({"status": "error", "msg": "ไม่พบเจ้าของตู้ในระบบ!"})
        target_password = occupant.password
        target_feature_vector = occupant.feature_vector
        target_user_id = occupant.user_id
    else:
        cursor.execute("SELECT * FROM Licenses WHERE user_id = ? AND locker_id = ?", (session['user_id'], locker_id))
        if not cursor.fetchone() and session['role'] != 'Admin':
            return jsonify({"status": "error", "msg": "คุณไม่มีสิทธิ์ใช้งานตู้นี้!"})
        cursor.execute("SELECT password, feature_vector FROM Users WHERE user_id = ?", (session['user_id'],))
        row = cursor.fetchone()
        target_password = row.password
        target_feature_vector = row.feature_vector

    if method == 'PIN':
        if not check_password_hash(target_password, pin):
            if current_status == 'Occupied':
                cursor.execute("INSERT INTO Alerts (alert_id, alert_type, alert_time, alert_status, intruder_image, locker_id) VALUES (?, ?, ?, ?, ?, ?)", (int(datetime.now().timestamp()%1000000), 'Failed Scan', datetime.now(), 'Pending', f"Wrong PIN on Locker {locker_id}", locker_id))
                conn.commit()
            return jsonify({"status": "error", "msg": "รหัส PIN ไม่ถูกต้อง!"})
            
    elif method == 'FACE':
        if not target_feature_vector or target_feature_vector == '':
            return jsonify({"status": "error", "msg": "คุณยังไม่ได้ลงทะเบียนใบหน้าในระบบ!"})
            
        image_data = data.get('image_data', '')
        try:
            encodings, _ = process_incoming_face(image_data)
            
            if not encodings or len(encodings) == 0:
                return jsonify({"status": "error", "msg": "AI มองไม่เห็นใบหน้า กรุณาขยับหน้าให้ชัดเจน!"})
                
            incoming_face_vector = encodings[0]
            saved_face_vector = np.array(json.loads(target_feature_vector))
            
            matches = face_recognition.compare_faces([saved_face_vector], incoming_face_vector, tolerance=0.5)
            
            if not matches[0]:
                if current_status == 'Occupied':
                    cursor.execute("INSERT INTO Alerts (alert_id, alert_type, alert_time, alert_status, intruder_image, locker_id) VALUES (?, ?, ?, ?, ?, ?)", (int(datetime.now().timestamp()%1000000), 'Failed Scan', datetime.now(), 'Pending', f"Face mismatch on Locker {locker_id}", locker_id))
                    conn.commit()
                return jsonify({"status": "error", "msg": "ใบหน้าไม่ตรงกับข้อมูล"})
                
        except Exception as e:
            return jsonify({"status": "error", "msg": f"AI Error: {str(e)}"})

    if current_status == 'Available':
        cursor.execute("UPDATE Lockers SET status = 'Occupied' WHERE locker_id = ?", (locker_id,))
        cursor.execute("INSERT INTO Access_Logs (log_id, access_time, access_method, user_id, locker_id) VALUES (?, ?, ?, ?, ?)", (log_id, datetime.now(), method, session['user_id'], locker_id))
        conn.commit()
        return jsonify({"status": "success", "msg": f"✅ เปิดตู้สำเร็จด้วยระบบ {method}!"})
    elif current_status == 'Occupied':
        if action == 'finish':
            cursor.execute("UPDATE Lockers SET status = 'Available' WHERE locker_id = ?", (locker_id,))
            cursor.execute("INSERT INTO Access_Logs (log_id, access_time, access_method, user_id, locker_id) VALUES (?, ?, ?, ?, ?)", (log_id, datetime.now(), method+'-Return', target_user_id, locker_id))
            conn.commit()
            return jsonify({"status": "success", "msg": "✅ ยืนยันตัวตนสำเร็จ คืนตู้เรียบร้อย"})
        else:
            cursor.execute("INSERT INTO Access_Logs (log_id, access_time, access_method, user_id, locker_id) VALUES (?, ?, ?, ?, ?)", (log_id, datetime.now(), method+'-Cont', target_user_id, locker_id))
            conn.commit()
            return jsonify({"status": "success", "msg": "✅ ยืนยันตัวตนสำเร็จ ใช้งานตู้ต่อได้"})

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'Admin': return redirect(url_for('index'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT A.log_id, A.access_time, A.access_method, U.username, A.locker_id FROM Access_Logs A LEFT JOIN Users U ON A.user_id = U.user_id ORDER BY A.access_time DESC")
    logs = cursor.fetchall()
    cursor.execute("SELECT alert_id, alert_type, alert_time, alert_status, intruder_image, locker_id FROM Alerts ORDER BY alert_time DESC")
    alerts_data = cursor.fetchall()
    conn.close()
    return render_template('admin_dashboard.html', logs=logs, alerts=alerts_data, username=session['username'])

@app.route('/admin_license')
def admin_license():
    if session.get('role') != 'Admin': return redirect(url_for('index'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username FROM Users WHERE role != 'Admin'")
    users = cursor.fetchall()
    cursor.execute("SELECT locker_id, location FROM Lockers ORDER BY locker_id")
    lockers = cursor.fetchall()
    cursor.execute("SELECT L.user_id, U.username, L.locker_id, Lo.location FROM Licenses L JOIN Users U ON L.user_id = U.user_id JOIN Lockers Lo ON L.locker_id = Lo.locker_id ORDER BY U.username, L.locker_id")
    licenses = cursor.fetchall()
    conn.close()
    return render_template('admin_license.html', username=session['username'], users=users, lockers=lockers, licenses=licenses)

@app.route('/grant_license', methods=['POST'])
def grant_license():
    if session.get('role') != 'Admin': return redirect(url_for('index'))
    user_id = request.form['user_id']
    locker_ids = request.form.getlist('locker_ids') 
    conn = get_db_connection()
    cursor = conn.cursor()
    success_count = 0
    for lid in locker_ids:
        cursor.execute("SELECT * FROM Licenses WHERE user_id=? AND locker_id=?", (user_id, lid))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO Licenses (user_id, locker_id) VALUES (?, ?)", (user_id, lid))
            success_count += 1
    conn.commit(); conn.close()
    flash(f"✅ เพิ่มสิทธิ์สำเร็จ {success_count} รายการ!", "success")
    return redirect(url_for('admin_license'))

@app.route('/revoke_licenses', methods=['POST'])
def revoke_licenses():
    if session.get('role') != 'Admin': return redirect(url_for('index'))
    license_pairs = request.form.getlist('licenses_to_revoke')
    conn = get_db_connection()
    cursor = conn.cursor()
    for pair in license_pairs:
        uid, lid = pair.split(',')
        cursor.execute("DELETE FROM Licenses WHERE user_id=? AND locker_id=?", (uid, lid))
    conn.commit(); conn.close()
    flash(f"✅ เพิกถอนสิทธิ์เรียบร้อย {len(license_pairs)} รายการ", "success")
    return redirect(url_for('admin_license'))

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM Users WHERE user_id = ?", (session['user_id'],))
        if check_password_hash(cursor.fetchone()[0], request.form['old_password']) and request.form['new_password'] == request.form['conf_password']:
            cursor.execute("UPDATE Users SET password = ? WHERE user_id = ?", (generate_password_hash(request.form['new_password']), session['user_id']))
            conn.commit(); flash("เปลี่ยนรหัสผ่านสำเร็จ!", "success")
        else: flash("รหัสผ่านไม่ถูกต้อง หรือรหัสใหม่ไม่ตรงกัน", "error")
        conn.close(); return redirect(url_for('index'))
    return render_template('change_password.html')

@app.route('/change_username', methods=['GET', 'POST'])
def change_username():
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM Users WHERE user_id = ?", (session['user_id'],))
        if check_password_hash(cursor.fetchone()[0], request.form['password']):
            cursor.execute("UPDATE Users SET username = ? WHERE user_id = ?", (request.form['new_username'], session['user_id']))
            conn.commit(); session['username'] = request.form['new_username']
            flash(f"เปลี่ยนชื่อเป็น {request.form['new_username']} สำเร็จ!", "success")
        else: flash("รหัสผ่านไม่ถูกต้อง", "error")
        conn.close(); return redirect(url_for('index'))
    return render_template('change_username.html')

@app.route('/report_issue', methods=['POST'])
def report_issue():
    conn = get_db_connection()
    cursor = conn.cursor()
    issue_msg = f"User {session['user_id']} reported: {request.form['issue_text']}"
    cursor.execute("INSERT INTO Alerts (alert_id, alert_type, alert_time, alert_status, intruder_image, locker_id) VALUES (?, ?, ?, ?, ?, ?)", (int(datetime.now().timestamp()%1000000), 'User Report', datetime.now(), 'Pending', issue_msg[:99], 101))
    conn.commit(); conn.close(); flash("ส่งแจ้งปัญหาเรียบร้อยแล้ว", "success"); return redirect(url_for('index'))

@app.route('/update_locker_status', methods=['POST'])
def update_locker_status():
    if session.get('role') != 'Admin': return redirect(url_for('index'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Lockers SET status = ? WHERE locker_id = ?", (request.form['status'], request.form['locker_id']))
    conn.commit(); conn.close(); return redirect(url_for('index'))

@app.route('/virtual_locker')
def virtual_locker():
    if 'logged_in' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT locker_id, location, status FROM Lockers")
    lockers = cursor.fetchall()
    conn.close()
    return render_template('virtual_locker.html', lockers=lockers)

@app.route('/admin_users', methods=['GET', 'POST'])
def admin_users():
    if session.get('role') != 'Admin': return redirect(url_for('index'))
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        action = request.form.get('action')
        target_user_id = request.form.get('user_id')
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        try:
            if action == 'add':
                hashed_pw = generate_password_hash(password)
                cursor.execute("INSERT INTO Users (user_id, username, password, role) VALUES (?, ?, ?, ?)", (target_user_id, username, hashed_pw, role))
                flash("✅ เพิ่มผู้ใช้ใหม่สำเร็จ!", "success")
            elif action == 'edit':
                if password: 
                    hashed_pw = generate_password_hash(password)
                    cursor.execute("UPDATE Users SET username = ?, password = ?, role = ? WHERE user_id = ?", (username, hashed_pw, role, target_user_id))
                else:
                    cursor.execute("UPDATE Users SET username = ?, role = ? WHERE user_id = ?", (username, role, target_user_id))
                flash("✅ แก้ไขข้อมูลผู้ใช้สำเร็จ!", "success")
            elif action == 'delete':
                cursor.execute("DELETE FROM Licenses WHERE user_id = ?", (target_user_id,))
                cursor.execute("UPDATE Access_Logs SET user_id = NULL WHERE user_id = ?", (target_user_id,))
                cursor.execute("DELETE FROM Users WHERE user_id = ?", (target_user_id,))
                flash("✅ ลบผู้ใช้สำเร็จ!", "success")
            conn.commit()
        except Exception as e:
            flash(f"❌ เกิดข้อผิดพลาด: {e}", "error")
        return redirect(url_for('admin_users'))

    cursor.execute("SELECT user_id, username, role FROM Users")
    users = cursor.fetchall()
    conn.close()
    return render_template('admin_users.html', username=session['username'], users=users, user_id=session.get('user_id'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)