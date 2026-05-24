import requests
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# diccionario para convertir el nombre bonito del aeropuerto a su codigo IATA
CIUDADES_IATA = {
    "Madrid Barajas": "MAD",
    "Barcelona El Prat": "BCN",
    "Palma de Mallorca": "PMI",
    "Málaga Costa del Sol": "AGP",
    "Alicante Elche": "ALC",
    "Gran Canaria": "LPA",
    "Tenerife Sur": "TFS",
    "Valencia": "VLC",
    "Sevilla": "SVQ",
    "Bilbao": "BIO",
    "Ibiza": "IBZ",
    "Lanzarote": "ACE",
    "Fuerteventura": "FUE",
    "Menorca": "MAH",
    "Santiago de Compostela": "SCQ",
    # Inglaterra
    "London Heathrow": "LHR",
    "London Gatwick": "LGW",
    "Manchester": "MAN",
    # Portugal
    "Lisboa": "LIS",
    "Oporto": "OPO",
    "Faro": "FAO",
    # Marruecos
    "Casablanca Mohammed V": "CMN",
    "Marrakech Menara": "RAK",
    "Tánger Ibn Battouta": "TNG",
    # Italia
    "Roma Fiumicino": "FCO",
    "Milán Malpensa": "MXP",
    "Nápoles": "NAP",
    # Francia
    "París Charles de Gaulle": "CDG",
    "París Orly": "ORY",
    "Marsella": "MRS",
    # Alemania
    "Frankfurt": "FRA",
    "Múnich": "MUC",
    "Berlín Brandenburg": "BER",
}

SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")

@st.cache_data(ttl=300)
def buscar_programacion_comercial(origen_nombre, destino_nombre, fecha_str):
    dep_iata = CIUDADES_IATA.get(origen_nombre)
    arr_iata = CIUDADES_IATA.get(destino_nombre)

    if not dep_iata or not arr_iata or not SERPAPI_KEY:
        return []

    try:
        r = requests.get(
            "https://serpapi.com/search.json",
            params={
                "engine":        "google_flights",
                "departure_id":  dep_iata,
                "arrival_id":    arr_iata,
                "outbound_date": fecha_str,
                "type":          "2",
                "currency":      "EUR",
                "hl":            "es",
                "api_key":       SERPAPI_KEY,
            },
            timeout=10,
        )
    except Exception as e:
        st.error(f"Error al conectar con Google Flights: {e}")
        return []

    if r.status_code != 200:
        st.error(f"Error en la API de vuelos ({r.status_code})")
        return []

    data = r.json()

    # mostrar error de SerpApi si lo hay
    if "error" in data:
        st.error(f"SerpApi: {data['error']}")
        return []

    vuelos = []
    horas_vistas = set()

    for oferta in data.get("best_flights", []) + data.get("other_flights", []):
        flights = oferta.get("flights", [])
        if not flights:
            continue

        # usar primer segmento (hora de salida del origen)
        segmento = flights[0]
        hora_str = segmento.get("departure_airport", {}).get("time", "")
        if not hora_str or len(hora_str) < 16:
            continue

        hora_texto = hora_str[11:16]  # "HH:MM"
        if hora_texto in horas_vistas:
            continue

        h = int(hora_texto[:2])
        m = int(hora_texto[3:5])

        escala = len(flights) > 1
        vuelos.append({
            "linea":       segmento.get("airline", "—"),
            "vuelo":       segmento.get("flight_number", "N/A").replace(" ", ""),
            "hora_salida": hora_texto,
            "hora_int":    h,
            "minuto_int":  m,
            "estado":      "scheduled",
            "precio":      oferta.get("price"),
            "escala":      escala,
        })
        horas_vistas.add(hora_texto)

    vuelos.sort(key=lambda x: (x["hora_int"], x["minuto_int"]))
    return vuelos
