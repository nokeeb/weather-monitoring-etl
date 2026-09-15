from pathlib import Path
PROJECT_ROOT=Path(__file__).resolve().parent.parent
import sys
import uuid
import logging
import datetime
sys.path.insert(0,str(PROJECT_ROOT))
from src import extract,database,transform,load
def main():
    run_id=uuid.uuid4()
    logging.basicConfig(filename=PROJECT_ROOT/'logs'/'fail_log.log',level=logging.INFO)
    logging.info(f"run_id={run_id} Pipeline started\n")
    with database.get_connection('weather_etl_db') as conn:
        load.create_audit_row(conn,run_id)
        locations=database.read_locations(conn)
    records_extracted=0
    valid_records=list()
    try:
        
        for location in locations:
            location_name=location[1]
            logging.info(f'run_id={run_id} Processing city={location_name}')
            extracted=extract.extract(location,run_id)
            logging.info(f'run_id={run_id} Raw API response saved for city={location_name}')
            records_extracted+=1
            transformed=transform.transform(extracted['raw_content'],location,run_id,extracted['extracted_at'],extracted['file_path'])
            valid_records.append(transformed)
            logging.info(f'run_id={run_id} Record validated for city={location_name}\n')
        logging.info(f'run_id={run_id} Extracted raw responses={records_extracted}')
        logging.info(f'run_id={run_id} Valid records={len(valid_records)}')

        rows_inserted=load.insert_observations(conn,valid_records)
        logging.info(f'run_id={run_id} Loaded records={rows_inserted}')
    except Exception as e:
        logging.critical(f'run_id={run_id} Error: {e}')

    if rows_inserted==3:       
        status='SUCCESS'
    elif rows_inserted==0:
        status='FAILED'
    else:
        status='PARTIAL'

    load.update_audit_row(conn,status,records_extracted,rows_inserted,None,run_id)
    logging.info(f'''run_id={run_id} Pipeline finished with status={status}\n
    --------------------------------------------------------------------------------------------''')


    if status=='FAILED':
        return 1
    else:
        return 0
    


if __name__=="__main__":
    main()