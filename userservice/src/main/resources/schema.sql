-- Create database schema for User Service

-- Drop tables if they exist (for development purposes)
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

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_external_id ON users(external_id);
CREATE INDEX idx_users_role_id ON users(role_id);
CREATE INDEX idx_users_delete_at ON users(delete_at);
CREATE INDEX idx_roles_role_name ON roles(role_name);
CREATE INDEX idx_roles_delete_at ON roles(delete_at);

-- Add comments to tables and columns
COMMENT ON TABLE roles IS 'Table to store user roles and permissions';
COMMENT ON COLUMN roles.role_name IS 'Unique name of the role (Student, Instructor, Admin)';
COMMENT ON COLUMN roles.description IS 'Description of the role and its permissions';

COMMENT ON TABLE users IS 'Table to store user information';
COMMENT ON COLUMN users.external_id IS 'External identifier from Moodle or other systems';
COMMENT ON COLUMN users.email IS 'User email address (unique)';
COMMENT ON COLUMN users.name IS 'User full name';
COMMENT ON COLUMN users.avatar_url IS 'URL to user avatar image';
COMMENT ON COLUMN users.role_id IS 'Foreign key reference to roles table';
