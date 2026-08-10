from pathlib import Path
from dotenv import load_dotenv
import os
PROJECT_ROOT=Path(__file__).resolve().parent.parent
RAW_DATA_DIR=PROJECT_ROOT/'data'/'raw'
LOG_DIR=PROJECT_ROOT/'logs'
SCHEMA_DIR=PROJECT_ROOT/'sql'
OPEN_METEO_URL='https://api.open-meteo.com/v1/forecast'
load_dotenv(PROJECT_ROOT/'.env')
PG_HOST=os.getenv('PG_HOST','localhost')
PG_PORT=os.getenv('PG_PORT','5432')
PG_ADMIN_DB=os.getenv('PG_ADMIN_DB','postgres')
PG_DBNAME=os.getenv('PG_DBNAME','weather_etl_db')
PG_USER=os.getenv('PG_USER','postgres')
PG_PASSWORD=os.getenv('PG_PASSWORD','changeme')





