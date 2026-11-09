import duckdb, pandas as pd
from openpyxl import load_workbook
from openpyxl.worksheet.table import Table, TableStyleInfo

con = duckdb.connect('data/processed/rental.duckdb', read_only=True)
out = 'powerbi/rental_stress_model.xlsx'

db_tables = ['dim_lga', 'dim_date', 'fact_rent', 'fact_income', 'fact_wage',
             'mart_ratio', 'early_warning', 'dq_log']

with pd.ExcelWriter(out, engine='openpyxl', date_format='yyyy-mm-dd',
                    datetime_format='yyyy-mm-dd') as xw:
    for t in db_tables:
        con.sql(f'SELECT * FROM {t}').df().to_excel(xw, sheet_name=t, index=False)
    pd.read_csv('data/processed/forecast.csv').to_excel(xw, sheet_name='forecast', index=False)
    pd.read_csv('data/processed/forecast_series.csv', parse_dates=['quarter_end']) \
      .to_excel(xw, sheet_name='forecast_series', index=False)
    (pd.read_csv('data/processed/sensitivity.csv')
       .melt(id_vars='threshold_pct', var_name='income_factor', value_name='lgas_at_or_above')
       .to_excel(xw, sheet_name='sensitivity', index=False))

# Power BI imports Excel data most reliably when each sheet is a formatted table
wb = load_workbook(out)
for ws in wb.worksheets:
    ref = f'A1:{ws.cell(row=ws.max_row, column=ws.max_column).coordinate}'
    tab = Table(displayName=ws.title, ref=ref)
    tab.tableStyleInfo = TableStyleInfo(name='TableStyleLight1', showRowStripes=False)
    ws.add_table(tab)
wb.save(out)
print('Wrote', out)