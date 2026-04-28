-- Clean VGM Assets Database Schema

-- 1️⃣ Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS vgm_assets;
USE vgm_assets;

-- 2️⃣ Drop tables if they already exist (fresh start)
DROP TABLE IF EXISTS maintenance_log;
DROP TABLE IF EXISTS assets;

-- 3️⃣ Create the assets table
CREATE TABLE assets (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    priority INT NOT NULL,
    status VARCHAR(50) NOT NULL,
    date_returned DATE,
    completed BOOLEAN DEFAULT FALSE
);

-- 4️⃣ Create the maintenance log table (optional)
CREATE TABLE maintenance_log (
    log_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    asset_id INT NOT NULL,
    description TEXT,
    date_logged DATE,
    CONSTRAINT fk_asset FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
);

-- 5️⃣ Reset auto-increment counters (optional)
ALTER TABLE assets AUTO_INCREMENT = 1;
ALTER TABLE maintenance_log AUTO_INCREMENT = 1;