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


# fechas
today = datetime.today().strftime("%Y-%m-%d")
start_date = f"{datetime.today().year}-01-01"


for i, (city, coords) in enumerate(CITIES.items()):

    lat = coords["lat"]
    lon = coords["lon"]

    url_weather = (
        f"{BASE_URL}"
        f"?latitude={lat}"
        f"&longitude={lon}"
        f"&start_date={start_date}"
        f"&end_date={today}"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        f"&timezone=auto"
    )

    weather_data = api_request(url_weather)

    results = []

    for j, date in enumerate(weather_data["daily"]["time"]):

        record = {
            "city": city,
            "date": date,
            "temp_max": weather_data["daily"]["temperature_2m_max"][j],
            "temp_min": weather_data["daily"]["temperature_2m_min"][j],
            "precipitation": weather_data["daily"]["precipitation_sum"][j]
        }

        results.append(record)

    mode = "w" if i == 0 else "a"

    data_writing(WEATHER_PATH, results, mode)