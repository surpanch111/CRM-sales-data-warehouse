-- Build dim_date covering all engage_date and close_date values,
-- extending one year on each side as a buffer for date filters in Power BI.

TRUNCATE TABLE warehouse.dim_date CASCADE;

WITH bounds AS (
    SELECT
        LEAST(MIN(engage_date), MIN(close_date)) - INTERVAL '1 year' AS min_d,
        GREATEST(MAX(engage_date), MAX(close_date)) + INTERVAL '1 year' AS max_d
    FROM staging.sales_pipeline
    WHERE engage_date IS NOT NULL OR close_date IS NOT NULL
),
date_series AS (
    SELECT generate_series(min_d::DATE, max_d::DATE, '1 day'::INTERVAL)::DATE AS d
    FROM bounds
)
INSERT INTO warehouse.dim_date (
    date_key, full_date, year, quarter, month, month_name,
    day, day_of_week, day_name, week_of_year, is_weekend
)
SELECT
    TO_CHAR(d, 'YYYYMMDD')::INT  AS date_key,
    d                            AS full_date,
    EXTRACT(YEAR    FROM d)::INT AS year,
    EXTRACT(QUARTER FROM d)::INT AS quarter,
    EXTRACT(MONTH   FROM d)::INT AS month,
    TRIM(TO_CHAR(d, 'Month'))    AS month_name,
    EXTRACT(DAY     FROM d)::INT AS day,
    EXTRACT(ISODOW  FROM d)::INT AS day_of_week,
    TRIM(TO_CHAR(d, 'Day'))      AS day_name,
    EXTRACT(WEEK    FROM d)::INT AS week_of_year,
    EXTRACT(ISODOW  FROM d) IN (6, 7) AS is_weekend
FROM date_series;