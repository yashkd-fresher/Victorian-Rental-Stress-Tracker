import duckdb, sys

con = duckdb.connect('data/processed/rental.duckdb', read_only=True)
print(con.sql(sys.argv[1]).df().to_string())