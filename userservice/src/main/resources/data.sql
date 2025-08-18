-- Insert sample data for User Service

-- Insert roles
INSERT INTO roles (role_name, description, create_at, update_at) VALUES
('ADMIN', 'System administrator with full access to all features', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('INSTRUCTOR', 'Teacher or educator who can create and manage courses', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('STUDENT', 'Student who can enroll in courses and view learning materials', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Insert sample users
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
('moodle_11', 'frank.martinez@university.edu', 'Frank Martinez', 'https://example.com/avatars/frank.jpg', 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('moodle_12', 'grace.anderson@university.edu', 'Grace Anderson', 'https://example.com/avatars/grace.jpg', 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- Users without external IDs (direct registration)
(NULL, 'teacher1@example.com', 'Jane Teacher', NULL, 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(NULL, 'student1@example.com', 'Mark Student', NULL, 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(NULL, 'student2@example.com', 'Lisa Learning', NULL, 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
