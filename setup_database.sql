-- SWMS Database Setup Script
-- Run this in MySQL Workbench or MySQL Command Line Client

-- Create the database
CREATE DATABASE IF NOT EXISTS swms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Show databases to confirm creation
SHOW DATABASES LIKE 'swms_db';

-- Optional: Create a dedicated user for SWMS (recommended for production)
-- CREATE USER 'swms_user'@'localhost' IDENTIFIED BY 'your_secure_password';
-- GRANT ALL PRIVILEGES ON swms_db.* TO 'swms_user'@'localhost';
-- FLUSH PRIVILEGES;

-- Use the database
USE swms_db;

-- Show that database is empty (no tables yet - Django will create them)
SHOW TABLES;
