from dotenv import load_dotenv
import psycopg2
from pathlib import Path
import os

def main():
    BASE_DIR=Path(__file__).resolve().parent.parent
    load_dotenv(BASE_DIR/'.env')
    admin_conn=None
    admin_cur=None
    conn=None
    cur=None
    pg_host=os.getenv("PG_HOST","localhost")
    pg_port=os.getenv("PG_PORT","5432")
    pg_admin_db=os.getenv("PG_ADMIN_DB","postgres")
    pg_dbname=os.getenv("PG_DBNAME","weather_etl_db")
    pg_user=os.getenv("PG_USER","postgres")
    pg_password=os.getenv("PG_PASSWORD","changeme")
    try:
        admin_conn=psycopg2.connect(
        dbname=pg_admin_db,
        host=pg_host,
        user=pg_user,
        port=pg_port,
        password=pg_password
        )
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
        with psycopg2.connect(dbname=pg_dbname,user=pg_user,password=pg_password,host=pg_host,port=pg_port) as conn:
            cur=conn.cursor()
            with open(BASE_DIR/'sql'/'001_schema.sql','r') as file:
                schema_script=file.read()

            cur.execute(schema_script)

            with open(BASE_DIR/'sql'/'002_seed_locations.sql','r') as file:
                location_script=file.read()

            cur.execute(location_script)
            print('Database initialization completed successfully.')
            
    except Exception as e:
        print(f'Error occurred:{e}')

    finally:
        if conn:
            conn.close()

if __name__=='__main__':
    main()