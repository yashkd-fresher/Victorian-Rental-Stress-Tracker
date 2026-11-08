import pandas as pd
import duckdb

raw = pd.read_excel('data/raw/634502b.xlsx', sheet_name='Data1')

vic_cols = [c for c in raw.columns if 'Victoria' in str(c) and 'Index' in str(c)]
print('Victoria column(s) found:', vic_cols)
assert len(vic_cols) == 1, 'Expected exactly one Victoria index column; send me the printed list'

wpi = raw[[raw.columns[0], vic_cols[0]]].iloc[9:].copy()   # skip the 9 metadata rows
wpi.columns = ['period', 'index_value']
wpi['index_value'] = pd.to_numeric(wpi['index_value'], errors='coerce')
wpi = wpi.dropna()
wpi['date_key'] = (pd.to_datetime(wpi['period'].astype(str), format='mixed')
                     .dt.to_period('Q').dt.end_time.dt.normalize())

con = duckdb.connect('data/processed/rental.duckdb')
con.execute('''
    CREATE OR REPLACE TABLE fact_wage AS
    SELECT CAST(date_key AS DATE) AS date_key, index_value
    FROM wpi
    WHERE date_key >= DATE '2019-03-31'
''')
print(con.sql('SELECT * FROM fact_wage ORDER BY date_key DESC LIMIT 5'))