-- Build fact_sales by joining staging pipeline to dim surrogate keys.
-- Truncate-and-rebuild: simple, correct, idempotent.

TRUNCATE TABLE warehouse.fact_sales;

INSERT INTO warehouse.fact_sales (
    opportunity_id, account_key, product_key, agent_key,
    engage_date_key, close_date_key, deal_stage, close_value, days_to_close
)
SELECT
    sp.opportunity_id,
    da.account_key,
    dp.product_key,
    dsa.agent_key,
    CASE WHEN sp.engage_date IS NOT NULL
         THEN TO_CHAR(sp.engage_date, 'YYYYMMDD')::INT END AS engage_date_key,
    CASE WHEN sp.close_date IS NOT NULL
         THEN TO_CHAR(sp.close_date, 'YYYYMMDD')::INT END  AS close_date_key,
    sp.deal_stage,
    sp.close_value,
    CASE
        WHEN sp.engage_date IS NOT NULL AND sp.close_date IS NOT NULL
        THEN (sp.close_date - sp.engage_date)
    END AS days_to_close
FROM staging.sales_pipeline sp
LEFT JOIN warehouse.dim_account     da  ON da.account_name  = sp.account
JOIN      warehouse.dim_product     dp  ON dp.product_name  = sp.product
JOIN      warehouse.dim_sales_agent dsa ON dsa.agent_name   = sp.sales_agent
WHERE sp.opportunity_id IS NOT NULL;

-- Refresh planner statistics so future queries pick good plans
ANALYZE warehouse.fact_sales;
ANALYZE warehouse.dim_account;
ANALYZE warehouse.dim_product;
ANALYZE warehouse.dim_sales_agent;
ANALYZE warehouse.dim_date;