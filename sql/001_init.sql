-- create extensions, schemas, and tables

-- Enable required extensions that ship with postgis image
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS hstore;

-- H3 is optional and requires pre-installation via PGXN or custom build.
-- Uncomment once the extension is installed in the Postgres image.
-- CREATE EXTENSION IF NOT EXISTS h3;
-- CREATE EXTENSION IF NOT EXISTS h3_postgis;

-- Create OSM schema (osm2pgsql will use this)
CREATE SCHEMA IF NOT EXISTS osm;
