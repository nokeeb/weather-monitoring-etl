import requests
import json
import config
grad_seher={'city_name':'SARAJEVO','latitude':-1390132901309.8563,'longitude':18.4131}
grad_seher_al_dobar={'city_name':'SARAJEVO','latitude':43.8563,'longitude':18.4131}
def extract(location,run_id):
    print(type(location['city_name']))
    request_string=f'{config.OPEN_METEO_URL}'
    parameters={"current":"temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,weather_code",
                    "temperature_unit":"celsius",
                    "wind_speed_unit":"kmh",
                    "timezone":"UTC",
                    "forecast_days":"1"}
    try:
        parameters["latitude"]=location['latitude']
        parameters['longitude']=location['longitude']
        response=requests.get(request_string,params=parameters,timeout=30)
        if not response.ok:
            response.raise_for_status()

        response_content=response.json()
        with open(config.PROJECT_ROOT/'data'/'raw'/f'{run_id}_{location['city_name'].lower()}.json','w',encoding='utf-8') as file:
            json.dump(response_content,file)
        file_path=config.PROJECT_ROOT/'data'/'raw'/f'{run_id}_{location['city_name'].lower()}.json'
        json.info={'raw_content':response_content,'file_path':file_path}
        return json.info
    
    except Exception as e:
        print(f'Error occured:{e}')
