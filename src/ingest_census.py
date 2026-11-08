import pandas as pd
import duckdb

g02 = pd.read_csv('data/raw/census/2021Census_G02_VIC_LGA.csv')
geo = pd.read_excel('data/raw/census/geog_desc.xlsx', sheet_name='2021_ASGS_Non_ABS_Structures')

lga = geo[geo['ASGS_Structure'] == 'LGA'][['Census_Code_2021', 'Census_Name_2021']]
lga.columns = ['LGA_CODE_2021', 'lga_raw']

df = g02.merge(lga, on='LGA_CODE_2021', how='left')
df['lga_name'] = df['lga_raw'].str.replace(r'(\s*\([^)]*\))+$', '', regex=True).str.strip()
df.columns = df.columns.str.lower()
df = df.dropna(subset=['lga_name'])
df = df[['lga_code_2021', 'lga_name', 'median_tot_hhd_inc_weekly', 'median_rent_weekly']]

con = duckdb.connect('data/processed/rental.duckdb')
con.execute('CREATE OR REPLACE TABLE stg_census_g02 AS SELECT * FROM df')

print('Census LGAs loaded:', len(df))
print()
print('Rent LGAs with NO Census match (these need the mapping file):')
print(con.sql('''
    SELECT DISTINCT TRIM(r.lga) AS rent_lga
    FROM stg_rent_raw r
    LEFT JOIN stg_census_g02 c ON TRIM(r.lga) = c.lga_name
    WHERE c.lga_name IS NULL AND r.row_type = 'council'
    ORDER BY 1
'''))