CREATE OR REPLACE TABLE mart_ratio AS
WITH base AS (
  SELECT index_value AS base_index
  FROM fact_wage
  WHERE date_key = DATE '2021-09-30'
),
wage AS (
  SELECT w.date_key, w.index_value / b.base_index AS wage_mult
  FROM fact_wage w CROSS JOIN base b
),
rent_all AS (
  SELECT lga_key, date_key, median_rent, new_lettings
  FROM fact_rent
  WHERE dwelling_type = 'all properties'
)
SELECT r.lga_key, r.date_key, r.median_rent, r.new_lettings,
       r.new_lettings >= 30                                   AS reliable,
       i.census_income_2021 * w.wage_mult                     AS est_income,
       r.median_rent / (i.census_income_2021 * w.wage_mult)   AS rent_to_income
FROM rent_all r
JOIN fact_income i USING (lga_key)
JOIN wage w USING (date_key)
WHERE r.date_key >= DATE '2019-03-31';