import psycopg2

DB_CONFIG = {
    "host": "104.236.5.115",
    "port": 15432,
    "dbname": "repositorio_leads",
    "user": "mbgRepositorio",
    "password": "Tw2629Hq9X1k"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)
