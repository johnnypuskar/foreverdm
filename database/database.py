from src.db_access import Database

db = Database("test")

db.query("DROP TABLE IF EXISTS test_table")
db.query("CREATE TABLE test_table (id serial PRIMARY KEY, num integer, data varchar);")