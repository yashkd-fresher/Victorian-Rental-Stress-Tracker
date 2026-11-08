import duckdb

con = duckdb.connect('data/processed/rental.duckdb', read_only=True)
tables = ['dim_lga', 'dim_date', 'fact_rent', 'fact_income', 'fact_wage',
          'mart_ratio', 'early_warning', 'dq_log']
for t in tables:
    con.execute(f"COPY {t} TO 'data/processed/{t}.csv' (HEADER, DELIMITER ',')")
    print('Exported', t)