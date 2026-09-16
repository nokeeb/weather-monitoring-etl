import psycopg2
from pathlib import Path
import os
PROJECT_ROOT=Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0,str(PROJECT_ROOT))
from src import config,database
import logging

def main():
    admin_conn=None
    admin_cur=None
    conn=None
    cur=None
    try:
        admin_conn=database.get_connection(config.PG_ADMIN_DB)
        admin_conn.autocommit=True  
        admin_cur=admin_conn.cursor()
        admin_cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{config.PG_DBNAME}'")
        exists=admin_cur.fetchone()
        if not exists:
            admin_cur.execute(f'CREATE DATABASE {config.PG_DBNAME}')
            print('Database created successfully !')
        else:
            print('Database already exists !')
    except Exception as e:
        logging.error(f'Database error occured: {e}')
        sys.exit(1)

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
        logging.error(f'Database error occured: {e}')
        sys.exit(1)
    finally:
        if conn:
            conn.close()
            

if __name__=='__main__':
    main()