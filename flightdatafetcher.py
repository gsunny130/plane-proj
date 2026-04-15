from opensky_api import OpenSkyApi, TokenManager
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

def get_callsign(box):
    callsign = ''
    api = OpenSkyApi(token_manager=TokenManager.from_json_file("credentials.json"))
    s = api.get_states(bbox=box)
    states = s.states
    try:
        callsign = states[0].callsign
        velocity = states[0].velocity
        icao24 = states[0].icao24
        return [callsign, velocity, icao24]
    except:
        print("No planes right now")
        return []

def get_info(callsign):
    access_key = os.getenv("AVI_ACCESS_KEY")
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
    return output

def get_aircraft(icao24, output):
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
    return output

def main():
    # just hard coding the area I can see from my window
    lamin = 39.879181
    lomin = -75.191631
    lamax = 39.895382
    lomax = -75.119362
    south_phl = [lamin, lamax, lomin, lomax]

    # load cache file if it exists
    if os.path.exists('flight_cache.json'):
        with open('flight_cache.json', 'r') as f:
            flight_cache = json.load(f)
    else:
        flight_cache = {}

    callsign_etc = get_callsign(box=south_phl)

    if not callsign_etc:
        return("No planes right now") 
    callsign = callsign_etc[0]
    velocity = callsign_etc[1]
    icao24 = callsign_etc[2]
    if callsign in flight_cache.keys():
        return flight_cache[callsign]

    output = get_info(callsign=callsign)
    if not output:
        return("No flight data found")
    
    output = get_aircraft(icao24=icao24, output=output)

    flight_cache[callsign] = output
    with open('flight_cache.json', 'w') as f:
        json.dump(flight_cache, f)
    return output

if __name__ == "__main__":
    print(main())
    

   
    



