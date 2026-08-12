from pathlib import Path
PROJECT_ROOT=Path(__file__).resolve().parent.parent
import sys
import pprint
import uuid
sys.path.insert(0,str(PROJECT_ROOT))
from src import extract,database,transform,load
def main():
    with database.get_connection('weather_etl_db') as conn:
        locations=database.read_locations(conn)
    run_id=uuid.uuid4()
    valid_records=list()
    records_extracted=0
    for location in locations:
        kurac=extract.extract(location,run_id)
        records_extracted+=1
        transformirani_kurac=transform.transform(kurac['raw_content'],location,run_id,kurac['extracted_at'],kurac['file_path'])
        valid_records.append(transformirani_kurac)
    load.create_audit_row(conn,run_id)
    rows_inserted=load.insert_observations(conn,valid_records)
    if rows_inserted==3:       
        status='SUCCESS'
    elif rows_inserted==0:
        status='FAILED'
    else:
        status='PARTIAL'
        
    load.update_audit_row(conn,status,records_extracted,rows_inserted,None,run_id)



if __name__=="__main__":
    main()