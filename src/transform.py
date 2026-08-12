from datetime import datetime,timezone
from pathlib import Path
PROJECT_ROOT=Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0,str(PROJECT_ROOT))
def transform(raw_json,location,run_id,extracted_at,raw_file_path):
    if 'current' not in raw_json:
        raise Exception("Missing 'current'")
    try:
        current=raw_json['current']
        if current['time'] is not None:
            time=current['time']
        time=datetime.fromisoformat(time).astimezone(timezone.utc)
        temperature_c=current['temperature_2m']
        relative_humidity_pct=current['relative_humidity_2m']
        surface_pressure_hpa=current['surface_pressure']
        wind_speed_kmh=current['wind_speed_10m']
        weather_code=current['weather_code']


        psql_record={"run_id":run_id,"location_id":location[0],"observed_at":time,
                    "extracted_at":extracted_at,"temperature_c":temperature_c,
                    "relative_humidity_pct":relative_humidity_pct,"surface_pressure_hpa":surface_pressure_hpa,
                    "wind_speed_kmh":wind_speed_kmh,"weather_code":weather_code,"raw_file_path":str(raw_file_path)}

                
        return psql_record
    except Exception as e:
        raise e(f'{e}')