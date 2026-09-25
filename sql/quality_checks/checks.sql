-- ============================================================
-- Data quality checks for the warehouse
-- A query returning rows = a failure. The Python runner aggregates results.
-- Each check is named so failures show up clearly in logs.
-- ============================================================

-- ---------- Check 1: minimum row counts (catches empty loads) ----------
SELECT 'staging.accounts is empty'        AS check_name, NULL::TEXT AS detail
WHERE (SELECT COUNT(*) FROM staging.accounts) = 0
UNION ALL
SELECT 'staging.products is empty', NULL
WHERE (SELECT COUNT(*) FROM staging.products) = 0
UNION ALL
SELECT 'staging.sales_pipeline is empty', NULL
WHERE (SELECT COUNT(*) FROM staging.sales_pipeline) = 0
UNION ALL
SELECT 'staging.sales_teams is empty', NULL
WHERE (SELECT COUNT(*) FROM staging.sales_teams) = 0
UNION ALL
SELECT 'warehouse.fact_sales is empty', NULL
WHERE (SELECT COUNT(*) FROM warehouse.fact_sales) = 0

-- ---------- Check 2: row count parity staging vs warehouse ----------
-- The bug we just hit. If pipeline rows are dropped silently, this fails.
UNION ALL
SELECT
    'row count drift staging -> warehouse',
    'staging=' || (SELECT COUNT(*) FROM staging.sales_pipeline)::TEXT
        || ' fact=' || (SELECT COUNT(*) FROM warehouse.fact_sales)::TEXT
WHERE (SELECT COUNT(*) FROM staging.sales_pipeline)
    <> (SELECT COUNT(*) FROM warehouse.fact_sales)

-- ---------- Check 3: no duplicate primary keys in fact ----------
UNION ALL
SELECT
    'duplicate opportunity_id',
    opportunity_id || ' (' || COUNT(*)::TEXT || ' copies)'
FROM warehouse.fact_sales
GROUP BY opportunity_id
HAVING COUNT(*) > 1

-- ---------- Check 4: orphan products (would have caught GTXPro) ----------
UNION ALL
SELECT
    'orphan product reference in pipeline',
    sp.product || ' (' || COUNT(*)::TEXT || ' rows)'
FROM staging.sales_pipeline sp
LEFT JOIN warehouse.dim_product p ON p.product_name = sp.product
WHERE p.product_key IS NULL AND sp.product IS NOT NULL
GROUP BY sp.product

-- ---------- Check 5: orphan sales agents ----------
UNION ALL
SELECT
    'orphan sales_agent reference in pipeline',
    sp.sales_agent || ' (' || COUNT(*)::TEXT || ' rows)'
FROM staging.sales_pipeline sp
LEFT JOIN warehouse.dim_sales_agent a ON a.agent_name = sp.sales_agent
WHERE a.agent_key IS NULL AND sp.sales_agent IS NOT NULL
GROUP BY sp.sales_agent

-- ---------- Check 6: business rule — Won deals must have close_value ----------
UNION ALL
SELECT
    'Won deal with NULL close_value',
    opportunity_id
FROM warehouse.fact_sales
WHERE deal_stage = 'Won' AND close_value IS NULL

-- ---------- Check 7: business rule — close_date >= engage_date ----------
UNION ALL
SELECT
    'close_date before engage_date',
    sp.opportunity_id
FROM staging.sales_pipeline sp
WHERE sp.close_date IS NOT NULL
  AND sp.engage_date IS NOT NULL
  AND sp.close_date < sp.engage_date

-- ---------- Check 8: deal_stage must be in expected set ----------
UNION ALL
SELECT
    'unexpected deal_stage value',
    deal_stage || ' (' || COUNT(*)::TEXT || ' rows)'
FROM warehouse.fact_sales
WHERE deal_stage NOT IN ('Won', 'Lost', 'Engaging', 'Prospecting')
GROUP BY deal_stage

-- ---------- Check 9: close_value should be non-negative ----------
UNION ALL
SELECT
    'negative close_value',
    opportunity_id || ' (' || close_value::TEXT || ')'
FROM warehouse.fact_sales
WHERE close_value < 0

-- ---------- Check 10: no future close_dates (data freshness sanity) ----------
UNION ALL
SELECT
    'close_date in the future',
    sp.opportunity_id || ' (' || sp.close_date::TEXT || ')'
FROM staging.sales_pipeline sp
WHERE sp.close_date > CURRENT_DATE;