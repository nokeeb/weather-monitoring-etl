import psycopg2.extras
from datetime import datetime,timezone
def create_audit_row(conn,run_id):
    psycopg2.extras.register_uuid()
    started_at=datetime.now(timezone.utc).replace(microsecond=0) 
    status='RUNNING'
    records_extracted=0
    records_loaded=0
    with conn.cursor() as cur:
        try:
            cur.execute("""INSERT INTO weather.pipeline_runs
            (run_id,started_at,status,records_extracted,records_loaded)
            VALUES(%s,%s,%s,%s,%s)""",
            [run_id,started_at,status,records_extracted,records_loaded])
            conn.commit()
        except Exception:
            raise

def insert_observations(conn,records):
    psycopg2.extras.register_uuid()

    inserted_rows=0
    try:
        with conn.cursor() as cur: 
            for record in records:
                cur.execute("""INSERT INTO weather.observations
                (run_id,location_id,observed_at,
                extracted_at,temperature_c,relative_humidity_pct,
                surface_pressure_hpa,wind_speed_kmh,weather_code,
                raw_file_path) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT(location_id,observed_at)
                DO NOTHING""" ,list(record.values()))
                if cur.rowcount==1:
                    inserted_rows+=1

            conn.commit()
            return inserted_rows

    except Exception:
        conn.rollback()
        raise

def update_audit_row(conn,status,records_extracted,records_loaded,error_message,run_id):
    finished_at=datetime.now(timezone.utc).replace(microsecond=0)
    cur=conn.cursor()
    cur.execute("""UPDATE weather.pipeline_runs 
    SET finished_at=%s,status=%s,records_extracted=%s,
    records_loaded=%s,error_message=%s WHERE run_id=%s""",
    [finished_at,status,records_extracted,records_loaded,error_message,run_id])
    conn.commit()