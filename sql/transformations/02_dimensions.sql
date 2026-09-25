-- Build dim_account, dim_product, dim_sales_agent from staging using upserts.
-- ON CONFLICT preserves surrogate keys across reloads — fact references stay valid.

-- ---------- dim_account ----------
INSERT INTO warehouse.dim_account (
    account_name, sector, year_established, revenue,
    employees, office_location, subsidiary_of
)
SELECT
    account, sector, year_established, revenue,
    employees, office_location, subsidiary_of
FROM staging.accounts
WHERE account IS NOT NULL
ON CONFLICT (account_name) DO UPDATE SET
    sector           = EXCLUDED.sector,
    year_established = EXCLUDED.year_established,
    revenue          = EXCLUDED.revenue,
    employees        = EXCLUDED.employees,
    office_location  = EXCLUDED.office_location,
    subsidiary_of    = EXCLUDED.subsidiary_of,
    loaded_at        = NOW();

-- ---------- dim_product ----------
INSERT INTO warehouse.dim_product (product_name, series, sales_price)
SELECT product, series, sales_price
FROM staging.products
WHERE product IS NOT NULL
ON CONFLICT (product_name) DO UPDATE SET
    series      = EXCLUDED.series,
    sales_price = EXCLUDED.sales_price,
    loaded_at   = NOW();

-- ---------- dim_sales_agent ----------
INSERT INTO warehouse.dim_sales_agent (agent_name, manager, regional_office)
SELECT sales_agent, manager, regional_office
FROM staging.sales_teams
WHERE sales_agent IS NOT NULL
ON CONFLICT (agent_name) DO UPDATE SET
    manager         = EXCLUDED.manager,
    regional_office = EXCLUDED.regional_office,
    loaded_at       = NOW();