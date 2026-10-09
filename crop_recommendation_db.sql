CREATE DATABASE crop_recommendation;
-- Use the same password as DB_PASSWORD in crop_recommendation/.env
CREATE USER agrosmart WITH PASSWORD 'change-me';
ALTER ROLE agrosmart SET client_encoding TO 'utf8';
ALTER ROLE agrosmart SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE crop_recommendation TO agrosmart;
