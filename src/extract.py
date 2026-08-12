import requests
import json
from . import config
from datetime import datetime,timezone



def extract(location,run_id):
    request_string=f'{config.OPEN_METEO_URL}'
    parameters={"current":"temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,weather_code",
                    "temperature_unit":"celsius",
                    "wind_speed_unit":"kmh",
                    "timezone":"UTC",
                    "forecast_days":"1"}
    
    parameters["latitude"]=location[3]
    parameters['longitude']=location[4]
    extracted_at=datetime.now(timezone.utc).replace(microsecond=0)
        
    response=requests.get(request_string,params=parameters,timeout=30)
    response.raise_for_status()

    response_content=response.json()
    with open(config.PROJECT_ROOT/'data'/'raw'/f'{run_id}_{location[1].lower()}.json','w',encoding='utf-8') as file:
        json.dump(response_content,file)
    file_path=config.PROJECT_ROOT/'data'/'raw'/f'{run_id}_{location[1].lower()}.json'


    json_info={'raw_content':response_content,'file_path':file_path,'extracted_at':extracted_at}
        

    return json_info
    
    



