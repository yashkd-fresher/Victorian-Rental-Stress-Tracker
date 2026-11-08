import duckdb, pathlib

con = duckdb.connect('data/processed/rental.duckdb')
for f in sorted(pathlib.Path('sql').glob('*.sql')):
    print('Running', f.name)
    try:
        con.execute(f.read_text())
    except Exception:
        print('FAILED in', f.name)
        raise
print('All SQL finished')