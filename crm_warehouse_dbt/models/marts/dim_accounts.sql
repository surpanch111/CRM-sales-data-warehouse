SELECT
    account,
    sector,
    revenue,
    employees,
    office_location,

    CASE
        WHEN revenue >= 1000000 THEN 'Enterprise'
        WHEN revenue >= 250000 THEN 'Mid-Market'
        ELSE 'Small Business'
    END AS account_tier

FROM {{ ref('stg_accounts') }}

WHERE revenue IS NOT NULL