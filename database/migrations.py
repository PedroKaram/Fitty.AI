import yaml
import psycopg2

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

db_config = config["postgres"]

conn = psycopg2.connect(
    dbname = db_config["dbname"],
    user = db_config["user"],
    password = db_config["password"],
    host = db_config["host"],
    port = db_config["port"]
)

cur = conn.cursor()

create_table_query = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password TEXT NOT NULL
);
"""

cur.execute(create_table_query)
conn.commit()

cur.close()
conn.close()

print("Tabela 'users' criada com sucesso.")
