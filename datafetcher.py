from opensky_api import OpenSkyApi, TokenManager
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

# just hard coding the area I can see from my window
lamin = 39.879181
lomin = -75.191631
lamax = 39.895382
lomax = -75.119362
south_phl = [lamin, lamax, lomin, lomax]

api = OpenSkyApi(token_manager=TokenManager.from_json_file("credentials.json"))
s = api.get_states(bbox=south_phl)
states = s.states

# initializing
callsign = ''
velocity = 0

try:
    callsign = states[0].callsign
    velocity = states[0].velocity
    icao24 = states[0].icao24
except:
    print("No planes right now")
    exit()

# additional info from aviationstack: departure airport and airline
access_key = os.getenv("AVI_ACCESS_KEY")

# load cache file if it exists
if os.path.exists('flight_cache.json'):
    with open('flight_cache.json', 'r') as f:
        flight_cache = json.load(f)
else:
    flight_cache = {}

if callsign:
    if callsign in flight_cache.keys():
        output = flight_cache[callsign]
    else:
        params = {'access_key' : access_key, 'flight_icao' : callsign}
        api_request = requests.get('https://api.aviationstack.com/v1/flights', params=params)
        try:
            api_request.raise_for_status()
            api_response = api_request.json()
            api_data = api_response['data'][0]
            departure_airport = api_data['departure']['airport']
            departure_iata = api_data['departure']['iata']
            airline = api_data['airline']['name']
            output = {
                'departure_airport': departure_airport,
                'departure_iata': departure_iata,
                'airline': airline
            }
        except (requests.exceptions.HTTPError, IndexError, KeyError) as e:
            print(f"no flight data found: {e}")
            output = {}

hexdb = "https://hexdb.io/api/v1/aircraft/" + icao24
hexdb_request = requests.get(hexdb)
try:
    hexdb_request.raise_for_status()
    hexdb_response = hexdb_request.json()
    aircraft_code = hexdb_response['Type']
    manufacturer = hexdb_response['Manufacturer']
    output['aircraft_code'] = aircraft_code
    output['aircraft_manufacturer'] = manufacturer
except requests.exceptions.HTTPError:
    print("aircraft not found")

flight_cache[callsign] = output
with open('flight_cache.json', 'w') as f:
    json.dump(flight_cache, f)

print(flight_cache[callsign])