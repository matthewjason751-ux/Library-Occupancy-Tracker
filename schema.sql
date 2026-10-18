CREATE DATABASE IF NOT EXISTS library_tracker;
USE library_tracker;

CREATE TABLE students (
    student_id VARCHAR(20) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE zones (
    zone_id INT AUTO_INCREMENT PRIMARY KEY,
    zone_name VARCHAR(30) UNIQUE NOT NULL,
    capacity INT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE visits (
    visit_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    zone_id INT NOT NULL,
    check_in_time DATETIME NOT NULL,
    check_out_time DATETIME NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (zone_id) REFERENCES zones(zone_id) ON DELETE CASCADE,
    INDEX idx_student (student_id),
    INDEX idx_check_in (check_in_time),
    INDEX idx_check_out (check_out_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE occupancy_snapshots (
    snapshot_id INT AUTO_INCREMENT PRIMARY KEY,
    snapshot_time DATETIME NOT NULL,
    total_occupancy INT NOT NULL,
    zone_id INT NULL,
    zone_occupancy INT NULL,
    FOREIGN KEY (zone_id) REFERENCES zones(zone_id) ON DELETE SET NULL,
    INDEX idx_snapshot_time (snapshot_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO zones (zone_name, capacity) VALUES 
('Silent', 50),
('General', 100),
('Discussion', 30),
('Computer', 40);

INSERT INTO students (student_id, full_name, password, is_active) VALUES 
('DEMO001', 'Alice Smith', 'demo123', TRUE),
('DEMO002', 'Bob Jones', 'demo123', TRUE),
('DEMO003', 'Charlie Brown', 'demo123', TRUE),
('DEMO004', 'Diana Prince', 'demo123', TRUE),
('DEMO005', 'Evan Wright', 'demo123', TRUE);
