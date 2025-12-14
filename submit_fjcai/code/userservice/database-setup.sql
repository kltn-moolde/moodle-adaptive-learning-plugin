-- ===============================================
-- USER SERVICE DATABASE SETUP FOR NEON POSTGRESQL
-- ===============================================
-- Execute this script in your Neon database console

-- Step 1: Create tables
-- ===============================================

-- Drop tables if they exist (be careful in production!)
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS roles CASCADE;

-- Create ROLES table
CREATE TABLE roles (
    id BIGSERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255),
    create_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delete_at TIMESTAMP NULL
);

-- Create USERS table
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    external_id VARCHAR(100) UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    avatar_url VARCHAR(500),
    role_id BIGINT NOT NULL,
    create_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delete_at TIMESTAMP NULL,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- Step 2: Create indexes for better performance
-- ===============================================
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_external_id ON users(external_id);
CREATE INDEX idx_users_role_id ON users(role_id);
CREATE INDEX idx_users_delete_at ON users(delete_at);
CREATE INDEX idx_roles_role_name ON roles(role_name);
CREATE INDEX idx_roles_delete_at ON roles(delete_at);

-- Step 3: Add comments
-- ===============================================
COMMENT ON TABLE roles IS 'Table to store user roles and permissions';
COMMENT ON COLUMN roles.role_name IS 'Unique name of the role (Student, Instructor, Admin)';
COMMENT ON COLUMN roles.description IS 'Description of the role and its permissions';

COMMENT ON TABLE users IS 'Table to store user information';
COMMENT ON COLUMN users.external_id IS 'External identifier from Moodle or other systems';
COMMENT ON COLUMN users.email IS 'User email address (unique)';
COMMENT ON COLUMN users.name IS 'User full name';
COMMENT ON COLUMN users.avatar_url IS 'URL to user avatar image';
COMMENT ON COLUMN users.role_id IS 'Foreign key reference to roles table';

-- Step 4: Insert initial roles
-- ===============================================
INSERT INTO roles (role_name, description, create_at, update_at) VALUES
('ADMIN', 'System administrator with full access to all features', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('INSTRUCTOR', 'Teacher or educator who can create and manage courses', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('STUDENT', 'Student who can enroll in courses and view learning materials', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Step 5: Insert sample users
-- ===============================================
INSERT INTO users (external_id, email, name, avatar_url, role_id, create_at, update_at) VALUES
-- Admin users
('moodle_1', 'admin@example.com', 'System Administrator', 'https://example.com/avatars/admin.jpg', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('moodle_2', 'john.admin@university.edu', 'John Smith', 'https://example.com/avatars/john.jpg', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- Instructor users
('moodle_3', 'dr.johnson@university.edu', 'Dr. Sarah Johnson', 'https://example.com/avatars/sarah.jpg', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('moodle_4', 'prof.williams@university.edu', 'Prof. Michael Williams', 'https://example.com/avatars/michael.jpg', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('moodle_5', 'ms.brown@university.edu', 'Ms. Emily Brown', 'https://example.com/avatars/emily.jpg', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- Student users
('moodle_6', 'alice.student@university.edu', 'Alice Thompson', 'https://example.com/avatars/alice.jpg', 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('moodle_7', 'bob.wilson@university.edu', 'Bob Wilson', 'https://example.com/avatars/bob.jpg', 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('moodle_8', 'carol.davis@university.edu', 'Carol Davis', 'https://example.com/avatars/carol.jpg', 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('moodle_9', 'david.miller@university.edu', 'David Miller', 'https://example.com/avatars/david.jpg', 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('moodle_10', 'eva.garcia@university.edu', 'Eva Garcia', 'https://example.com/avatars/eva.jpg', 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- Users without external IDs (direct registration)
(NULL, 'teacher1@example.com', 'Jane Teacher', NULL, 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(NULL, 'student1@example.com', 'Mark Student', NULL, 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(NULL, 'student2@example.com', 'Lisa Learning', NULL, 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Step 6: Verify the data
-- ===============================================
-- Check roles
SELECT * FROM roles ORDER BY id;

-- Check users
SELECT u.id, u.external_id, u.email, u.name, r.role_name 
FROM users u 
JOIN roles r ON u.role_id = r.id 
ORDER BY u.id;

-- Count users by role
SELECT r.role_name, COUNT(u.id) as user_count
FROM roles r
LEFT JOIN users u ON r.id = u.role_id AND u.delete_at IS NULL
WHERE r.delete_at IS NULL
GROUP BY r.id, r.role_name
ORDER BY r.id;

-- ===============================================
-- SETUP COMPLETE!
-- 
-- Your database is now ready for the User Service.
-- 
-- Next steps:
-- 1. Update application.properties with your Neon database connection details
-- 2. Run the Spring Boot application: mvn spring-boot:run
-- 3. Test the APIs at http://localhost:8081/api/
-- ===============================================
