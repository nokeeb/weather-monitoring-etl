import psycopg2
from pathlib import Path
PROJECT_ROOT=Path(__file__).resolve().parent.parent
from . import config
def get_connection(database_name):
    
    conn=psycopg2.connect(
    dbname=database_name,
    user=config.PG_USER,
    password=config.PG_PASSWORD,
    host=config.PG_HOST,
    port=config.PG_PORT  
    )
    return conn

def read_locations(connection):
    with connection.cursor() as cur:
        cur.execute("SELECT * FROM weather.locations")
        return cur.fetchall()

def execute_sql(file_name):
    PROJECT_ROOT=config.PROJECT_ROOT

    with open(PROJECT_ROOT/'sql'/file_name,'r') as file:
        command=file.read()
        return command
