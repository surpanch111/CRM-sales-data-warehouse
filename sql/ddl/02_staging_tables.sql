-- Staging: 1:1 mirrors of the four Maven CSVs.
-- All columns nullable, no FKs. Load-friendly.

DROP TABLE IF EXISTS staging.accounts CASCADE;
CREATE TABLE staging.accounts (
    account          TEXT,
    sector           TEXT,
    year_established INTEGER,
    revenue          NUMERIC(14, 2),    -- in millions of USD per data dictionary
    employees        INTEGER,
    office_location  TEXT,
    subsidiary_of    TEXT
);
COMMENT ON COLUMN staging.accounts.revenue IS 'Annual revenue in millions of USD';

DROP TABLE IF EXISTS staging.products CASCADE;
CREATE TABLE staging.products (
    product     TEXT,
    series      TEXT,
    sales_price NUMERIC(12, 2)
);
COMMENT ON COLUMN staging.products.sales_price IS 'Suggested retail price';

DROP TABLE IF EXISTS staging.sales_teams CASCADE;
CREATE TABLE staging.sales_teams (
    sales_agent     TEXT,
    manager         TEXT,
    regional_office TEXT
);

DROP TABLE IF EXISTS staging.sales_pipeline CASCADE;
CREATE TABLE staging.sales_pipeline (
    opportunity_id TEXT,
    sales_agent    TEXT,
    product        TEXT,
    account        TEXT,
    deal_stage     TEXT,
    engage_date    DATE,
    close_date     DATE,
    close_value    NUMERIC(14, 2)
);
COMMENT ON COLUMN staging.sales_pipeline.deal_stage  IS 'Prospecting > Engaging > Won/Lost';
COMMENT ON COLUMN staging.sales_pipeline.close_value IS 'Revenue from the deal (USD)';

CREATE INDEX idx_stg_pipeline_account ON staging.sales_pipeline(account);
CREATE INDEX idx_stg_pipeline_product ON staging.sales_pipeline(product);
CREATE INDEX idx_stg_pipeline_agent   ON staging.sales_pipeline(sales_agent);