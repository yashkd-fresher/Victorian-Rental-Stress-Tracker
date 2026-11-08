import re
import pandas as pd
import duckdb

PATH = 'data/raw/dffh_rents_jun2026.xlsx'
frames = []

for sheet in pd.ExcelFile(PATH).sheet_names:
    raw = pd.read_excel(PATH, sheet_name=sheet, header=None)

    periods = raw.iloc[1, 2:].ffill()      # Excel row 2: quarter labels
    measures = raw.iloc[2, 2:]             # Excel row 3: Count or Median
    body = raw.iloc[3:].copy()             # data starts at Excel row 4

    body[0] = body[0].ffill()              # region shows only on the first row of its group
    body = body[body[1].notna() & (body[1].astype(str).str.strip() != 'Group Total')]
    body = body.rename(columns={0: 'region', 1: 'lga'})

    long = body.melt(id_vars=['region', 'lga'], var_name='col', value_name='value')
    meta = pd.DataFrame({'col': periods.index,
                         'period': periods.values,
                         'measure': measures.astype(str).str.strip().str.lower().values})
    long = long.merge(meta, on='col')
    long['value'] = pd.to_numeric(long['value'], errors='coerce')

    wide = (long.pivot_table(index=['region', 'lga', 'period'], columns='measure',
                             values='value', aggfunc='first')
                .reset_index()
                .rename(columns={'count': 'new_lettings', 'median': 'median_rent'}))
    wide.columns.name = None

    m = re.match(r'(\d+)\s+bedroom\s+(\w+)', sheet.strip().lower())
    wide['dwelling_type'] = m.group(2) if m else 'all properties'
    wide['bedrooms'] = int(m.group(1)) if m else pd.NA
    frames.append(wide)

rent = pd.concat(frames, ignore_index=True)
rent['row_type'] = (rent['lga'].astype(str).str.strip()
                    .isin(['Metro', 'Non-Metro', 'Victoria'])
                    .map({True: 'summary', False: 'council'}))
rent['quarter_end'] = (pd.to_datetime(rent['period'].astype(str), format='mixed')
                         .dt.to_period('Q').dt.end_time.dt.normalize())
rent['bedrooms'] = rent['bedrooms'].astype('Int64')
rent = rent[['region', 'lga', 'row_type', 'dwelling_type', 'bedrooms', 'quarter_end',
             'median_rent', 'new_lettings']]

con = duckdb.connect('data/processed/rental.duckdb')
con.execute('CREATE OR REPLACE TABLE stg_rent_raw AS SELECT * FROM rent')

print('Council LGAs:', rent.loc[rent['row_type'] == 'council', 'lga'].nunique())
print(con.sql('''
    SELECT dwelling_type, bedrooms, COUNT(*) AS n_rows, COUNT(DISTINCT lga) AS lgas,
           MIN(quarter_end) AS first_q, MAX(quarter_end) AS last_q
    FROM stg_rent_raw GROUP BY 1, 2 ORDER BY 1, 2
'''))