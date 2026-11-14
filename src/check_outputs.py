import sys
import pandas as pd

ew = pd.read_csv('data/processed/early_warning.csv')
fc = pd.read_csv('data/processed/forecast.csv')
sens = pd.read_csv('data/processed/sensitivity.csv', index_col='threshold_pct')

checks = {
    'early_warning has 70 to 79 councils': 70 <= len(ew) <= 79,
    'one row per council': ew['lga_key'].is_unique,
    'statuses are valid': set(ew['status']) <= {'In stress', 'Early warning', 'Stable'},
    'ratios plausible (5% to 90%)': ew['rent_to_income_pct'].between(5, 90).all(),
    'In stress rows are at or above 30%': (ew.loc[ew['status'] == 'In stress', 'rent_to_income_pct'] >= 29.9).all(),
    'rows above 30.1% are In stress': (ew.loc[ew['rent_to_income_pct'] > 30.1, 'status'] == 'In stress').all(),
    'forecast has no missing values': not fc[['lga_key', 'forecast_4q_pct', 'backtest_mape_pct']].isna().any().any(),
    'forecast errors are not negative': (fc['backtest_mape_pct'] >= 0).all(),
    'sensitivity matches In stress count': int(sens.loc[30, '1.0']) == int((ew['status'] == 'In stress').sum()),
}
failed = 0
for name, ok in checks.items():
    print(('PASS  ' if ok else 'FAIL  ') + name)
    failed += (not ok)
sys.exit(1 if failed else 0)