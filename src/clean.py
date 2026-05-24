import os
import csv
import json


def json_to_csv(file_path):
    out = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line in ("[", "]"):
                continue
            guardar = json.loads(line)
            out.append({
                "city":           guardar.get("city"),
                "datetime":       guardar.get("datetime"),
                "temperature":    guardar.get("temperature"),
                "precipitation":  guardar.get("precipitation"),
                "wind_speed":     guardar.get("wind_speed"),
                "wind_direction": guardar.get("wind_direction"),
            })

    fieldnames = ["city", "datetime", "temperature", "precipitation", "wind_speed", "wind_direction"]

    os.makedirs("data/clean", exist_ok=True)

    with open("data/clean/weather_data.csv", "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(out)


if __name__ == "__main__":
    json_to_csv("data/raw/weather_data.json")
