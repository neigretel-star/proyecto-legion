def score_wind(speed_kmh):
    speed = float(speed_kmh)
    if speed <= 5:   return 100
    if speed <= 15:  return 100 - (speed - 5) * 4
    if speed <= 35:  return max(0, 60 - (speed - 15) * 3)
    return 0


def score_precipitation(mm):
    precip = float(mm)
    if precip == 0:  return 100
    if precip <= 1:  return max(0, 100 - precip * 40)
    if precip <= 5:  return max(0, 60 - (precip - 1) * 15)
    return 0


def score_temperature(celsius):
    temp = float(celsius)
    if 20 <= temp <= 25:  return 100
    if 15 <= temp < 20:   return 50 + (temp - 15) * 10
    if 25 < temp <= 33:   return max(0, 100 - (temp - 25) * 8)
    if 10 <= temp < 15:   return max(0, 50 - (15 - temp) * 5)
    return max(0, 36 - (temp - 33) * 4)


def composite_score(wind, precip, temp):
    return min(100.0, (wind * 0.40) + (precip * 0.30) + (temp * 0.30))


def score_to_rating(score):
    nota = round(score / 10, 1)
    if score >= 80: return nota, "Excelente", "#22c55e"
    if score >= 60: return nota, "Bueno",     "#84cc16"
    if score >= 40: return nota, "Regular",   "#f59e0b"
    return nota, "Malo", "#ef4444"


def score_flight(origin_weather, dest_weather):
    try:
        o_v = score_wind(origin_weather.get("wind_speed", 0))
        o_p = score_precipitation(origin_weather.get("precipitation", 0))
        o_t = score_temperature(origin_weather.get("temperature", 20))

        d_v = score_wind(dest_weather.get("wind_speed", 0))
        d_p = score_precipitation(dest_weather.get("precipitation", 0))
        d_t = score_temperature(dest_weather.get("temperature", 20))

        nota, etiqueta, color = score_to_rating(min(
            composite_score(o_v, o_p, o_t),
            composite_score(d_v, d_p, d_t),
        ))
        return {"rating": nota, "label": etiqueta, "color": color}
    except Exception:
        return {"rating": 0.0, "label": "Error", "color": "#333333"}
