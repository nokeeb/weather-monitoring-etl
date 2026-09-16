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

        if current['time'] is  None:
            raise Exception("Missing or null 'time' in current")
        time=datetime.fromisoformat(current['time']).replace(tzinfo=timezone.utc)

        if current['temperature_2m'] is not None and current['temperature_2m']>=-60 and current['temperature_2m']<=60 and type(current['temperature_2m']) is float:
            temperature_c=current['temperature_2m']
        else:
            raise ValueError("current['temperature_2m'] is invalid.")
        
        if current['relative_humidity_2m'] is not None and current['relative_humidity_2m']>=0 and current['relative_humidity_2m']<=100 and type(current['relative_humidity_2m']) is int:
            relative_humidity_pct=current['relative_humidity_2m']
        else:
            raise ValueError("current['relative_humidity_2m'] is invalid.")
        
        if current['surface_pressure'] is not None and current['surface_pressure']>=800 and current['surface_pressure']<=1100 and type (current['surface_pressure']) is float:
            surface_pressure_hpa=current['surface_pressure']
        else:
            raise ValueError("current['surface_pressure'] is invalid.")
        
        if current['wind_speed_10m'] is not None and current['wind_speed_10m']>=0 and type(current['wind_speed_10m']) is float:
            wind_speed_kmh=current['wind_speed_10m']
        else:
            raise ValueError("current['wind_speed_10m'] is invalid.")
        
        if current['weather_code'] is not None and type(current['weather_code']) is int:
            weather_code=current['weather_code']
        else:
            raise ValueError("current['weather_code'] is invalid.")

        psql_record={"run_id":run_id,"location_id":location[0],"observed_at":time,
                    "extracted_at":extracted_at,"temperature_c":temperature_c,
                    "relative_humidity_pct":relative_humidity_pct,"surface_pressure_hpa":surface_pressure_hpa,
                    "wind_speed_kmh":wind_speed_kmh,"weather_code":weather_code,"raw_file_path":str(raw_file_path)}

                
        return psql_record
    except Exception as e:
            raise