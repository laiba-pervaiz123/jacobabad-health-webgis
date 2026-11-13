-- ============================================================
-- Web GIS Midterm Project (MET418) - Jacobabad Medical Facilities
-- STEP A: In pgAdmin, right-click Databases > Create > Database
--         Name: jacobabad_medical
-- STEP B: Select that database > Tools > Query Tool > run this file
-- ============================================================

-- 1) Enable PostGIS (adds spatial data types and functions)
CREATE EXTENSION IF NOT EXISTS postgis;

-- 2) Create the table (geom stores each facility as a POINT in WGS84)
DROP TABLE IF EXISTS medical_facilities;

CREATE TABLE medical_facilities (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(150) NOT NULL,
    facility_type   VARCHAR(50)  NOT NULL,   -- Hospital, Clinic, Pharmacy ...
    category        VARCHAR(60)  NOT NULL,   -- grouped type used on the website
    contact         VARCHAR(30),
    address         TEXT,
    operating_hours VARCHAR(50),
    geom            GEOMETRY(Point, 4326) NOT NULL
);

-- 3) Spatial index (makes spatial queries fast)
CREATE INDEX idx_medical_facilities_geom
    ON medical_facilities USING GIST (geom);
