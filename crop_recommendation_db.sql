CREATE DATABASE crop_recommendation;
CREATE USER agrosmart WITH PASSWORD '5py';
ALTER ROLE agrosmart SET client_encoding TO 'utf8';
ALTER ROLE agrosmart SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE crop_recommendation TO agrosmart;
