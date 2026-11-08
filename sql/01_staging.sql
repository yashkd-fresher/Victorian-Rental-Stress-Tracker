CREATE OR REPLACE TABLE lga_name_map AS
SELECT * FROM read_csv_auto('reference/lga_name_map.csv', header = true);

CREATE OR REPLACE TABLE stg_rent AS
SELECT
  TRIM(region)                 AS region,
  TRIM(lga)                    AS lga_name,
  LOWER(TRIM(dwelling_type))   AS dwelling_type,
  bedrooms,
  CAST(quarter_end AS DATE)    AS quarter_end,
  median_rent,
  new_lettings
FROM stg_rent_raw
WHERE median_rent IS NOT NULL
  AND NOT isnan(median_rent)
  AND median_rent > 0
  AND row_type = 'council';
  
CREATE OR REPLACE TABLE stg_rent_summary AS
SELECT TRIM(lga) AS area, LOWER(TRIM(dwelling_type)) AS dwelling_type, bedrooms,
       CAST(quarter_end AS DATE) AS quarter_end, median_rent, new_lettings
FROM stg_rent_raw
WHERE row_type = 'summary' AND median_rent IS NOT NULL AND NOT isnan(median_rent);  

CREATE OR REPLACE TABLE stg_census AS
SELECT lga_name,
       median_tot_hhd_inc_weekly AS census_income_2021,
       median_rent_weekly        AS census_median_rent_2021
FROM stg_census_g02
WHERE median_tot_hhd_inc_weekly > 0;

CREATE OR REPLACE TABLE lga_match AS
SELECT DISTINCT r.lga_name AS rent_lga,
       COALESCE(m.census_lga, r.lga_name) AS census_lga
FROM stg_rent r
LEFT JOIN lga_name_map m ON r.lga_name = m.rent_lga;