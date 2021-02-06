import os
import requests
import base64
import json
import csv

from typing import List
from collections import namedtuple

StopLocation = namedtuple('StopLocation', 'name, id_, lat, lon, weight, track')
HEADER_KEYS = ['name', 'id', 'lat', 'lon', 'weight', 'track']


def get_access_token() -> str:
    vt_key = os.getenv('VT_KEY')
    vt_secret = os.getenv('VT_SECRET')

    assert vt_key is not None
    assert vt_secret is not None

    token = f'{vt_key}:{vt_secret}'
    encoded_token = base64.b64encode(token.encode('utf-8')).decode('utf-8')

    headers = {
        'Authorization': f'Basic {encoded_token}'
    }
    data = {
        'grant_type': 'client_credentials'
    }

    r = requests.post('https://api.vasttrafik.se:443/token', data=data, headers=headers)
    data = r.json()

    return data['access_token']


def fetch_all_stops_data(access_token: str) -> dict:
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'format': 'json'
    }

    r = requests.get('https://api.vasttrafik.se/bin/rest.exe/v2/location.allstops', headers=headers, params=params)

    return r.json()


def transform_data_into_stops(data: dict) -> List[StopLocation]:
    stop_locations = []

    for entry in data['LocationList']['StopLocation']:
        stop_location = StopLocation(
            entry['name'],
            entry['id'],
            entry['lat'],
            entry['lon'],
            int(entry['weight']),
            entry['track'] if 'track' in entry else None
        )

        stop_locations.append(stop_location)

    return stop_locations


def write_csv_file(stop_locations: List[StopLocation]):
    with open('./data/stops.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(HEADER_KEYS)

        for stop_location in stop_locations:
            writer.writerow([
                stop_location.name,
                stop_location.id_,
                stop_location.lat,
                stop_location.lon,
                stop_location.weight,
                stop_location.track
            ])


def write_json_file(stop_locations: List[StopLocation]):
    with open('./data/stops.json', 'w', encoding='utf-8') as f:
        data = [dict(zip(HEADER_KEYS, stop_location)) for stop_location in stop_locations]
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    access_token: str = get_access_token()
    data: dict = fetch_all_stops_data(access_token)
    stop_locations = transform_data_into_stops(data)

    print(f'len(stop_locations) = {len(stop_locations)}x')

    if not os.path.exists('./data/'):
        os.mkdir('./data/')

    write_csv_file(stop_locations)
    write_json_file(stop_locations)


if __name__ == "__main__":
    main()
