import requests
import json
import pandas as pd

DIVVY_STATION_URL = 'https://gbfs.divvybikes.com/gbfs/en/station_information.json'

res = requests.get(DIVVY_STATION_URL)
jsonres = res.json()

station_json = json.dumps(jsonres['data']['stations'])
station_status_df = pd.read_json(station_json)

cleaned_stationdata = station_status_df[['capacity', 'lat', 'lon', 'station_id', 'name', 'short_name']]
cleaned_stationdata.to_csv('station.csv')
