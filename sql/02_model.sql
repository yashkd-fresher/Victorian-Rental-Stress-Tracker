CREATE OR REPLACE TABLE dim_lga AS
SELECT ROW_NUMBER() OVER (ORDER BY lga_name) AS lga_key, lga_name, region
FROM (SELECT lga_name, MIN(region) AS region FROM stg_rent GROUP BY lga_name);

CREATE OR REPLACE TABLE dim_date AS
SELECT DISTINCT date_key,
       YEAR(date_key)    AS year,
       QUARTER(date_key) AS quarter,
       CAST(YEAR(date_key) AS VARCHAR) || '-Q' || CAST(QUARTER(date_key) AS VARCHAR) AS year_quarter
FROM (SELECT quarter_end AS date_key FROM stg_rent
      UNION
      SELECT date_key FROM fact_wage);

CREATE OR REPLACE TABLE fact_rent AS
SELECT l.lga_key, r.quarter_end AS date_key, r.dwelling_type, r.bedrooms,
       r.median_rent, r.new_lettings
FROM stg_rent r
JOIN dim_lga l ON r.lga_name = l.lga_name;

CREATE OR REPLACE TABLE fact_income AS
SELECT l.lga_key, c.census_income_2021, c.census_median_rent_2021
FROM lga_match m
JOIN dim_lga l ON m.rent_lga = l.lga_name
JOIN stg_census c ON m.census_lga = c.lga_name;

CREATE OR REPLACE TABLE dq_log AS
SELECT 'rent rows loaded (all)' AS check_name, COUNT(*) AS rows_affected FROM stg_rent_raw
UNION ALL
SELECT 'summary rows set aside (Metro, Non-Metro, Victoria)',
       COUNT(*) FROM stg_rent_raw WHERE row_type = 'summary'
UNION ALL
SELECT 'council rows dropped (no valid median)',
       (SELECT COUNT(*) FROM stg_rent_raw WHERE row_type = 'council') - (SELECT COUNT(*) FROM stg_rent)
UNION ALL
SELECT 'council LGAs in rent data', COUNT(*) FROM dim_lga
UNION ALL
SELECT 'LGAs with no Census income (excluded from ratios)',
       COUNT(*) FROM dim_lga l LEFT JOIN fact_income i USING (lga_key)
       WHERE i.lga_key IS NULL;