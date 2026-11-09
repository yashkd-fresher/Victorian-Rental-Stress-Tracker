import duckdb, pandas as pd

con = duckdb.connect('data/processed/rental.duckdb', read_only=True)
df = con.sql('''
    SELECT l.lga_name, m.median_rent, m.est_income
    FROM mart_ratio m JOIN dim_lga l USING (lga_key)
    WHERE m.date_key = (SELECT MAX(date_key) FROM mart_ratio)
''').df()

rows = []
for factor in [0.95, 1.00, 1.05]:              # income 5% lower, as estimated, 5% higher
    for threshold in [0.25, 0.27, 0.28, 0.30]:
        ratio = df['median_rent'] / (df['est_income'] * factor)
        rows.append({'income_factor': factor, 'threshold_pct': int(threshold * 100),
                     'lgas_at_or_above': int((ratio >= threshold).sum())})

out = (pd.DataFrame(rows)
         .pivot(index='threshold_pct', columns='income_factor', values='lgas_at_or_above'))
print(out)
out.to_csv('data/processed/sensitivity.csv')