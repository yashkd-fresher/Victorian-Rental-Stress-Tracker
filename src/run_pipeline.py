import subprocess, sys

steps = ['src/ingest_rent.py', 'src/ingest_wpi.py', 'src/ingest_census.py', 'src/run_sql.py',
         'src/validate.py', 'src/export.py', 'src/forecast.py', 'src/sensitivity.py',
         'src/check_outputs.py', 'src/make_powerbi_workbook.py']

for s in steps:
    print('==>', s)
    r = subprocess.run([sys.executable, s])
    if r.returncode != 0:
        print('Stopped at', s)
        sys.exit(r.returncode)
print('Pipeline complete.')