-- create extensions, schemas, and tables

-- Enable required extensions that ship with postgis image
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS hstore;

-- H3 requires the custom docker/postgis image which installs the extension via PGXN.
CREATE EXTENSION IF NOT EXISTS h3_postgis CASCADE;

-- Create OSM schema (osm2pgsql will use this)
CREATE SCHEMA IF NOT EXISTS osm;
