import duckdb, sys

con = duckdb.connect('data/processed/rental.duckdb', read_only=True)
checks = {
    'LGA count between 70 and 100': 'SELECT COUNT(*) BETWEEN 70 AND 100 FROM dim_lga',
    'no null estimated income': 'SELECT COUNT(*) = 0 FROM mart_ratio WHERE est_income IS NULL',
    'ratios plausible (0.05 to 0.90)': 'SELECT COUNT(*) = 0 FROM mart_ratio WHERE rent_to_income NOT BETWEEN 0.05 AND 0.90',
    'early_warning has rows': 'SELECT COUNT(*) > 0 FROM early_warning',
    'one early_warning row per LGA': 'SELECT COUNT(*) = COUNT(DISTINCT lga_key) FROM early_warning',
    'wage base quarter exists': "SELECT COUNT(*) = 1 FROM fact_wage WHERE date_key = DATE '2021-09-30'",
}
failed = 0
for name, sql in checks.items():
    ok = con.execute(sql).fetchone()[0]
    print(('PASS  ' if ok else 'FAIL  ') + name)
    failed += (not ok)
sys.exit(1 if failed else 0)

