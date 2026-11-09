import duckdb, numpy as np, pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

con = duckdb.connect('data/processed/rental.duckdb', read_only=True)
df = con.sql('''
    SELECT m.lga_key, l.lga_name, m.date_key, m.rent_to_income
    FROM mart_ratio m JOIN dim_lga l USING (lga_key)
    ORDER BY m.lga_key, m.date_key
''').df()
df['date_key'] = pd.to_datetime(df['date_key'])

full_q = pd.period_range(df['date_key'].min(), df['date_key'].max(), freq='Q')
future_q = pd.period_range(full_q[-1] + 1, periods=4, freq='Q')
summary, series, skipped = [], [], []

for (key, name), g in df.groupby(['lga_key', 'lga_name']):
    raw_s = g.set_index(g['date_key'].dt.to_period('Q'))['rent_to_income'].reindex(full_q)
    if raw_s.isna().iloc[-1]:
        skipped.append(name)          # no latest-quarter value, so do not forecast from stale data
        continue
    s = raw_s.interpolate(limit=2)    # short gaps in the middle are filled
    if s.isna().any():
        skipped.append(name)          # too many missing quarters to forecast
        continue
    y = s.values
    train, test = y[:-4], y[-4:]
    back = ExponentialSmoothing(train, trend='add').fit().forecast(4)
    mape = float(np.mean(np.abs((test - back) / test)))
    fc = ExponentialSmoothing(y, trend='add').fit().forecast(4)

    summary.append({'lga_key': key, 'lga_name': name,
                    'backtest_mape_pct': round(100 * mape, 1),
                    'forecast_4q_pct': round(100 * float(fc[-1]), 1),
                    'crosses_30pct': bool((fc >= 0.30).any()),
                    'forecast_reliable': bool(mape <= 0.05)})
    for p, v in zip(full_q, y):
        series.append({'lga_key': key, 'quarter_end': p.end_time.normalize().date(),
                       'rent_to_income_pct': round(100 * float(v), 1), 'series': 'actual'})
    for p, v in zip(future_q, fc):
        series.append({'lga_key': key, 'quarter_end': p.end_time.normalize().date(),
                       'rent_to_income_pct': round(100 * float(v), 1), 'series': 'forecast'})

out = pd.DataFrame(summary)
out.to_csv('data/processed/forecast.csv', index=False)
pd.DataFrame(series).to_csv('data/processed/forecast_series.csv', index=False)

print('LGAs forecast:', len(out), '| skipped:', skipped)
print('Median backtest MAPE (%):', out['backtest_mape_pct'].median())
print('Share with MAPE <= 5%:', round(100 * out['forecast_reliable'].mean()), '%')
print('LGAs forecast to cross 30%:', int(out['crosses_30pct'].sum()))