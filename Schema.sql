CREATE DATABASE Smart_Locker
GO

USE Smart_Locker
GO

CREATE TABLE [User] (
    user_id INT PRIMARY KEY,
    username NVARCHAR(50) NOT NULL,
    password NVARCHAR(255) NOT NULL,
    role NVARCHAR(10) NOT NULL,
    ref_image_path NVARCHAR(100),
    feature_vector NVARCHAR(MAX)
)

CREATE TABLE Locker (
    locker_id INT PRIMARY KEY,
    iot_device_id NVARCHAR(20),
    location NVARCHAR(50),
    status NVARCHAR(15) DEFAULT 'Available'
)

CREATE TABLE License (
    user_id INT,
    locker_id INT,
    PRIMARY KEY (user_id, locker_id),
    FOREIGN KEY (user_id) REFERENCES [User](user_id),
    FOREIGN KEY (locker_id) REFERENCES Locker(locker_id)
)

CREATE TABLE Access_Log (
    log_id INT PRIMARY KEY,
    access_time DATETIME DEFAULT GETDATE(),
    access_method NVARCHAR(20),
    captured_image NVARCHAR(100),
    user_id INT,
    locker_id INT,
    log_status NVARCHAR(10) DEFAULT 'Unread',
    FOREIGN KEY (user_id) REFERENCES [User](user_id),
    FOREIGN KEY (locker_id) REFERENCES Locker(locker_id)
)

CREATE TABLE Alert (
    alert_id INT PRIMARY KEY,
    alert_type NVARCHAR(30),
    alert_time DATETIME DEFAULT GETDATE(),
    alert_status NVARCHAR(10) DEFAULT 'Pending',
    intruder_image NVARCHAR(100),
    locker_id INT,
    FOREIGN KEY (locker_id) REFERENCES Locker(locker_id)
)