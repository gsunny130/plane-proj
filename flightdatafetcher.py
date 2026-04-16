from opensky_api import OpenSkyApi, TokenManager
import requests
import os
import json
from dotenv import load_dotenv
import time

load_dotenv()

def get_callsign(box, last_callsign):
    api = OpenSkyApi(token_manager=TokenManager.from_json_file("credentials.json"))
    s = api.get_states(bbox=box)
    states = s.states
    try:
        for state in states:
            if state.callsign == last_callsign:
                continue
            callsign = state.callsign
            velocity = state.velocity
            icao24 = state.icao24
            return [callsign, velocity, icao24]
        return []
    except:
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
        print(f"no aviationstack flight data found: {e}")
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

def format_output(output):
    output_string = "Departure Airport: " + output['departure_airport'] + "(" + output['departure_iata'] + ")\n"
    output_string += output['airline'] + ' ' + output.get('aircraft_manufacturer', '') + ' ' + output.get('aircraft_code', 'unknown aircraft')
    return output_string

def main():
    # just hard coding the area I can see from my window
    # took some trial and error using bboxfinder.com
    lamin = 39.878786
    lomin = -75.177126
    lamax = 39.892024
    lomax = -75.141592
    south_phl = [lamin, lamax, lomin, lomax]

    global last_callsign

    # load cache file if it exists
    if os.path.exists('flight_cache.json'):
        with open('flight_cache.json', 'r') as f:
            flight_cache = json.load(f)
    else:
        flight_cache = {}
    
    if os.path.exists('invalid_flight_cache.json'):
        with open('invalid_flight_cache.json', 'r') as f:
            invalid_flight_cache = json.load(f)
    else:
        invalid_flight_cache = []

    callsign_etc = get_callsign(box=south_phl, last_callsign=last_callsign)

    if not callsign_etc:
        return("No new planes right now") 
    callsign = callsign_etc[0]
    velocity = callsign_etc[1]
    icao24 = callsign_etc[2]

    # quit if it is the same plane we just saw
    # redundant now because of the edit I made to get_callsign function
    if callsign == last_callsign:
        return(f"Same plane again: {callsign}")
    # otherwise set last call sign as current call sign
    else:
        last_callsign = callsign

    if callsign in flight_cache.keys():
        output = flight_cache[callsign]
        output_string = format_output(output)
        return(output_string)
    if callsign in invalid_flight_cache:
        return (f"No flight information for {callsign}")

    output = get_info(callsign=callsign)
    if not output:
        print(callsign)
        invalid_flight_cache.append(callsign)
        with open('invalid_flight_cache.json', 'w') as f:
            json.dump(invalid_flight_cache, f)
        return("No output returned from aviationstack")
    
    output = get_aircraft(icao24=icao24, output=output)

    flight_cache[callsign] = output

    with open('flight_cache.json', 'w') as f:
        json.dump(flight_cache, f)

    output_string = format_output(output=output)
    return output_string


if __name__ == "__main__":
    last_callsign = ''
    while True:
        result = main()
        pushcut_url = os.getenv("PUSHCUT_URL")
        print(result)
        if result and not result.startswith("No"):
            requests.post(pushcut_url, json={"text": str(result)})
        time.sleep(20)
    

   
    



