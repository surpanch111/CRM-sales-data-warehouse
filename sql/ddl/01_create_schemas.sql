-- Two schemas: staging is reload-friendly raw, warehouse is the analytics layer
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS warehouse;

COMMENT ON SCHEMA staging   IS 'Raw 1:1 mirrors of source CSVs. Truncate-and-reload.';
COMMENT ON SCHEMA warehouse IS 'Cleaned star schema for analytics. Power BI connects here.';

-- GRANT USAGE, CREATE ON SCHEMA staging, warehouse TO crm_user;