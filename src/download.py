import os
import json
import datetime
import requests

from config import BASE_URL, CITIES, WEATHER_PATH

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


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


def parse_hourly(weather_data, city):
    results = []
    for j, time in enumerate(weather_data["hourly"]["time"]):
        results.append({
            "city":           city,
            "datetime":       time,
            "temperature":    weather_data["hourly"]["temperature_2m"][j],
            "precipitation":  weather_data["hourly"]["precipitation"][j],
            "wind_speed":     weather_data["hourly"]["windspeed_10m"][j],
            "wind_direction": weather_data["hourly"]["winddirection_10m"][j],
        })
    return results


def download_all():
    today = datetime.date.today()
    start = str(today - datetime.timedelta(days=7))
    end   = str(today - datetime.timedelta(days=2))

    for i, (city, coords) in enumerate(CITIES.items()):
        lat, lon = coords["lat"], coords["lon"]

        url_archive = (
            f"{ARCHIVE_URL}?latitude={lat}&longitude={lon}"
            f"&start_date={start}&end_date={end}"
            f"&hourly=temperature_2m,precipitation,windspeed_10m,winddirection_10m"
            f"&timezone=auto"
        )
        url_forecast = (
            f"{BASE_URL}?latitude={lat}&longitude={lon}"
            f"&forecast_days=16"
            f"&hourly=temperature_2m,precipitation,windspeed_10m,winddirection_10m"
            f"&timezone=auto"
        )

        results = parse_hourly(api_request(url_archive), city)
        results += parse_hourly(api_request(url_forecast), city)

        data_writing(WEATHER_PATH, results, mode="w" if i == 0 else "a")


if __name__ == "__main__":
    download_all()
