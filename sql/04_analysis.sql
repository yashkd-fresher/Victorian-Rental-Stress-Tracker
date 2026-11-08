CREATE OR REPLACE TABLE early_warning AS
WITH trend AS (
  SELECT lga_key, date_key, median_rent, new_lettings, reliable, est_income, rent_to_income,
         rent_to_income - LAG(rent_to_income, 4) OVER (PARTITION BY lga_key ORDER BY date_key) AS yoy_change,
         AVG(rent_to_income) OVER (PARTITION BY lga_key ORDER BY date_key
                                   ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_4q
  FROM mart_ratio
),
latest AS (
  SELECT * FROM trend
  WHERE date_key = (SELECT MAX(date_key) FROM mart_ratio)
)
SELECT l.lga_key, l.lga_name, l.region, t.date_key AS latest_quarter,
       t.median_rent, ROUND(t.est_income, 0) AS est_income,
       t.new_lettings, t.reliable,
       ROUND(100 * t.rent_to_income, 1) AS rent_to_income_pct,
       ROUND(100 * t.yoy_change, 1)     AS yoy_change_pts,
       ROUND(100 * t.rolling_4q, 1)     AS rolling_4q_pct,
       CASE WHEN t.rent_to_income >= 0.30 THEN 'In stress'
            WHEN t.rent_to_income >= 0.27 AND t.yoy_change > 0 THEN 'Early warning'
            ELSE 'Stable' END AS status,
       RANK() OVER (ORDER BY t.rent_to_income DESC)  AS stress_rank,
       NTILE(4) OVER (ORDER BY t.yoy_change DESC)    AS momentum_quartile
FROM latest t
JOIN dim_lga l USING (lga_key);