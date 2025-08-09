-- Initialize the messaging_app database
CREATE DATABASE IF NOT EXISTS messaging_app_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Grant privileges to the user
GRANT ALL PRIVILEGES ON messaging_app_db.* TO 'messaging_user'@'%';
FLUSH PRIVILEGES;

-- Use the database
USE messaging_app_db;

-- Create tables will be handled by Django migrations
