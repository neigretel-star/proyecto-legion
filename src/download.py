import os
import json
import requests
from datetime import datetime

from config import BASE_URL, CITIES, WEATHER_PATH


def api_request(url):

    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Error API: {response.status_code}")

    return response.json()


def data_writing(file_path, data, mode="w"):

    os.makedirs("data/raw", exist_ok=True)

    with open(file_path, mode, encoding="utf-8") as f:
        for element in data:
            f.write(json.dumps(element) + "\n")

    print(f"Se guardaron {len(data)} registros en {file_path}")


for i, (city, coords) in enumerate(CITIES.items()):

    lat = coords["lat"]
    lon = coords["lon"]

    url_weather = (
        f"{BASE_URL}"
        f"?latitude={lat}"
        f"&longitude={lon}"
        f"&current_weather=true"
    )

    weather_data = api_request(url_weather)

    weather_data["city"] = city
    weather_data["ingestion_time"] = datetime.utcnow().isoformat()

    mode = "w" if i == 0 else "a"

    data_writing(WEATHER_PATH, [weather_data], mode)