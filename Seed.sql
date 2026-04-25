-- เพิ่มผู้ใช้งาน 5 คน
INSERT INTO Users (user_id, username, password, role) VALUES 
(1, 'CPE', '123456', 'Admin'),
(10, 'ICT', '123456', 'Admin'),
(6901, 'SPU', '123456', 'User'),
(6902, 'Sky', '123456', 'User'),
(6903, 'Win', '123456', 'User')

-- เพิ่มตู้ล็อกเกอร์ 30 ตู้ (แบ่งเป็น 3 ชั้น)
DECLARE @i INT = 101
WHILE @i <= 110 BEGIN
    INSERT INTO Lockers (locker_id, location, status) VALUES (@i, 'Office Floor 1', 'Available')
    SET @i = @i + 1
END

SET @i = 201;
WHILE @i <= 210 BEGIN
    INSERT INTO Lockers (locker_id, location, status) VALUES (@i, 'Lab Floor 2', 'Available')
    SET @i = @i + 1
END

SET @i = 301;
WHILE @i <= 310 BEGIN
    INSERT INTO Lockers (locker_id, location, status) VALUES (@i, 'Workshop Floor 3', 'Available')
    SET @i = @i + 1
END

-- 1. มอบสิทธิ์ให้ CPE (1) เข้าใช้งานได้ทุกตู้ที่มีในระบบ
INSERT INTO Licenses (user_id, locker_id)
SELECT 1, locker_id FROM Lockers;

-- 2. มอบสิทธิ์ให้ ICT (10) เข้าใช้งานได้ทุกตู้ที่มีในระบบ
INSERT INTO Licenses (user_id, locker_id)
SELECT 10, locker_id FROM Lockers;

-- 3. มอบสิทธิ์ให้ SPU (6901) เข้าได้เฉพาะตู้ชั้น 1 (101-110) 
INSERT INTO Licenses (user_id, locker_id)
SELECT 6901, locker_id FROM Lockers 
WHERE locker_id BETWEEN 101 AND 110;

-- 4. มอบสิทธิ์ให้ Sky (6902) เข้าได้เฉพาะตู้ชั้น 2 (201-210) 
INSERT INTO Licenses (user_id, locker_id)
SELECT 6902, locker_id FROM Lockers 
WHERE locker_id BETWEEN 201 AND 210;

-- 5. มอบสิทธิ์ให้ Win (6903) เข้าได้เฉพาะตู้ชั้น 3 (301-310) 
INSERT INTO Licenses (user_id, locker_id)
SELECT 6903, locker_id FROM Lockers 
WHERE locker_id BETWEEN 301 AND 310;