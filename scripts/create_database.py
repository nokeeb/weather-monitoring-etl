import psycopg2
from pathlib import Path
import os
PROJECT_ROOT=Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0,str(PROJECT_ROOT))
from src import config,database,extract

def main():
    admin_conn=None
    admin_cur=None
    conn=None
    cur=None

    try:
        admin_conn=database.get_connection(config.PG_ADMIN_DB)
        admin_conn.autocommit=True  
        admin_cur=admin_conn.cursor()
        admin_cur.execute('DROP DATABASE IF EXISTS weather_etl_db')
        admin_cur.execute('CREATE DATABASE weather_etl_db')
        print('Database created successfully ! (or existed)')
    except Exception as e:
        print(f'Error occured:{e}')

    finally:
        if admin_cur:
            admin_cur.close()
        if admin_conn:
            admin_conn.close()

    try:
        with database.get_connection(config.PG_DBNAME) as conn:
            cur=conn.cursor()
            schema_file=database.execute_sql('001_schema.sql')
            cur.execute(schema_file)

            seed_file=database.execute_sql('002_seed_locations.sql')
            cur.execute(seed_file)
            
            print('Database initialization completed successfully.')

    except Exception as e:
        print(f'Error occurred:{e}')

    finally:
        if conn:
            conn.close()
            

if __name__=='__main__':
    main()