-- Warehouse: star schema. Surrogate keys, FKs, indexed for Power BI imports.

-- ---------- DIMENSIONS ----------

DROP TABLE IF EXISTS warehouse.dim_account CASCADE;
CREATE TABLE warehouse.dim_account (
    account_key       SERIAL PRIMARY KEY,
    account_name      TEXT UNIQUE NOT NULL,
    sector            TEXT,
    year_established  INTEGER,
    revenue           NUMERIC(14, 2),
    employees         INTEGER,
    office_location   TEXT,
    subsidiary_of     TEXT,
    loaded_at         TIMESTAMPTZ DEFAULT NOW()
);

DROP TABLE IF EXISTS warehouse.dim_product CASCADE;
CREATE TABLE warehouse.dim_product (
    product_key  SERIAL PRIMARY KEY,
    product_name TEXT UNIQUE NOT NULL,
    series       TEXT,
    sales_price  NUMERIC(12, 2),
    loaded_at    TIMESTAMPTZ DEFAULT NOW()
);

DROP TABLE IF EXISTS warehouse.dim_sales_agent CASCADE;
CREATE TABLE warehouse.dim_sales_agent (
    agent_key       SERIAL PRIMARY KEY,
    agent_name      TEXT UNIQUE NOT NULL,
    manager         TEXT,
    regional_office TEXT,
    loaded_at       TIMESTAMPTZ DEFAULT NOW()
);

DROP TABLE IF EXISTS warehouse.dim_date CASCADE;
CREATE TABLE warehouse.dim_date (
    date_key     INTEGER PRIMARY KEY,   -- YYYYMMDD as integer
    full_date    DATE NOT NULL UNIQUE,
    year         INTEGER NOT NULL,
    quarter      INTEGER NOT NULL,
    month        INTEGER NOT NULL,
    month_name   TEXT NOT NULL,
    day          INTEGER NOT NULL,
    day_of_week  INTEGER NOT NULL,
    day_name     TEXT NOT NULL,
    week_of_year INTEGER NOT NULL,
    is_weekend   BOOLEAN NOT NULL
);

-- ---------- FACT ----------

DROP TABLE IF EXISTS warehouse.fact_sales CASCADE;
CREATE TABLE warehouse.fact_sales (
    opportunity_id   TEXT PRIMARY KEY,
    account_key      INTEGER REFERENCES warehouse.dim_account(account_key),
    product_key      INTEGER NOT NULL REFERENCES warehouse.dim_product(product_key),
    agent_key        INTEGER NOT NULL REFERENCES warehouse.dim_sales_agent(agent_key),
    engage_date_key  INTEGER REFERENCES warehouse.dim_date(date_key),
    close_date_key   INTEGER REFERENCES warehouse.dim_date(date_key),
    deal_stage       TEXT NOT NULL,
    close_value      NUMERIC(14, 2),
    days_to_close    INTEGER,
    is_won           BOOLEAN GENERATED ALWAYS AS (deal_stage = 'Won') STORED,
    loaded_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_fact_account     ON warehouse.fact_sales(account_key);
CREATE INDEX idx_fact_product     ON warehouse.fact_sales(product_key);
CREATE INDEX idx_fact_agent       ON warehouse.fact_sales(agent_key);
CREATE INDEX idx_fact_engage_date ON warehouse.fact_sales(engage_date_key);
CREATE INDEX idx_fact_close_date  ON warehouse.fact_sales(close_date_key);
CREATE INDEX idx_fact_deal_stage  ON warehouse.fact_sales(deal_stage);