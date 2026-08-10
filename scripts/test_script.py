from pathlib import Path
PROJECT_ROOT=Path(__file__).resolve().parent.parent
import sys
import pprint
sys.path.insert(0,str(PROJECT_ROOT))
from src import extract,database,transform
from psycopg2.extras import execute_values

def main():
    with database.get_connection('weather_etl_db') as conn:
        locations=database.read_locations(conn)
        lokacija={"id":locations[0][0],"city_name":locations[0][1],"latitude":locations[0][3],"longitude":locations[0][4]}
        neki_json=extract.extract(lokacija,'c3d90b7b-2379-4b80-83b0-c5134106e891')
        raw_api_json=neki_json['raw_content']
        file_path=str(neki_json['file_path'])
        run_id=(file_path.split('\\')[-1].split('_')[0])
        extracted_at=neki_json['extracted_at']
        rekordinjo=transform.transform(raw_api_json,lokacija,run_id,extracted_at,file_path)
        print(rekordinjo)
    



if __name__=="__main__":
    main()