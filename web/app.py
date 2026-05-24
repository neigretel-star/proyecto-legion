import streamlit as st
import sys
import os
import json
import random
import datetime as _dt
from dotenv import load_dotenv

load_dotenv()

# --- RUTAS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
src_path = os.path.join(project_root, "src")

if src_path not in sys.path:
    sys.path.insert(0, src_path)

# --- IMPORTACIONES ---
try:
    from ayuda_weather import load_weather_csv, get_weather_at, get_available_dates, degrees_to_compass
    from flight_scoring import score_flight
    from avionstack import buscar_programacion_comercial, CIUDADES_IATA
except ModuleNotFoundError as e:
    st.error(f"Error crítico: No se encuentra el archivo en la carpeta src.")
    st.info(f"Python está buscando en: {src_path}")
    st.stop()

st.set_page_config(page_title="Legion Flight", layout="wide")

# --- USUARIOS JSON ---
USUARIOS_PATH = os.path.join(current_dir, "usuarios.json")

def cargar_usuarios():
    if os.path.exists(USUARIOS_PATH):
        with open(USUARIOS_PATH, "r") as f:
            return json.load(f)
    return {}

def guardar_usuarios(usuarios):
    with open(USUARIOS_PATH, "w") as f:
        json.dump(usuarios, f)

# --- SESSION STATE ---
if "favoritos" not in st.session_state:
    st.session_state["favoritos"] = []
if "rutas_favoritas" not in st.session_state:
    st.session_state["rutas_favoritas"] = []



def load_data():
    return load_weather_csv()

df_weather = load_data()
available_dates = get_available_dates(df_weather)

# Ciudad aleatoria por sesión para el hero
if "hero_city" not in st.session_state:
    st.session_state["hero_city"] = random.choice(list(CIUDADES_IATA.keys()))

hero_city = st.session_state["hero_city"]
hero_iata = CIUDADES_IATA[hero_city]

# --- HERO WEATHER (ciudad aleatoria, primera fecha disponible) ---
hero_weather = None
for try_hour in [12, 9, 15, 6, 0]:
    hero_weather = get_weather_at(df_weather, hero_city, available_dates[0], try_hour)
    if hero_weather:
        break

if hero_weather:
    h_wind_speed  = f"{hero_weather['wind_speed']} km/h"
    h_wind_dir    = degrees_to_compass(hero_weather['wind_direction'])
    h_temp        = f"{hero_weather['temperature']} °C"
    h_precip_mm   = hero_weather['precipitation']
    h_precip_str  = f"{h_precip_mm} mm"
    p = h_precip_mm
    h_precip_label = "Sin lluvia" if p == 0 else ("Lluvia ligera" if p <= 1 else ("Lluvia moderada" if p <= 5 else "Lluvia intensa"))
else:
    h_wind_speed = h_wind_dir = h_temp = h_precip_str = "—"
    h_precip_label = "Sin datos"

# --- CSS + NAVBAR ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Syne', sans-serif; color: #ffffff !important; }

    [data-testid="stMarkdownContainer"] p { color: #e8eaf0; }
    [data-testid="stText"] { color: #e8eaf0; }
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    [data-testid="stMetricLabel"] { color: #9ca3af !important; }
    [data-testid="stMetricDelta"] { color: #9ca3af !important; }
    label { color: #9ca3af !important; }
    p { color: #e8eaf0; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    [data-testid="stSidebar"]        { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stAppViewContainer"] { background-color: #06080f; }

    .navbar {
        position: fixed; top: 0; left: 0; width: 100%; z-index: 9999;
        background-color: #0e1117; border-bottom: 1px solid #2e2e2e;
        display: flex; align-items: center; justify-content: space-between;
        padding: 0.6rem 2rem; box-sizing: border-box;
    }
    .navbar-logo {
        font-family: 'Syne', sans-serif; font-size: 1.4rem; font-weight: 800; color: #fff;
    }
    .navbar-links { display: flex; gap: 2.5rem; align-items: center; }
    .navbar-links a { color: #c0c0c0; text-decoration: none; font-size: 0.95rem; font-weight: 500; }
    .navbar-links a:hover { color: #ffffff; }
    .navbar-right { display: flex; align-items: center; }
    .navbar-login {
        background: #2563eb; color: white !important; font-weight: 600 !important;
        padding: 0.42rem 1.1rem; border-radius: 8px;
        font-size: 0.9rem; text-decoration: none !important; white-space: nowrap;
    }
    .navbar-login:hover { background: #1d4ed8; }
    .block-container { padding-top: 4.5rem !important; }

    div.stButton > button {
        width: 100% !important; height: 3.2em !important;
        margin-top: 4px !important;
        background-color: #2563eb !important;
        color: white !important; font-weight: bold !important;
        border-radius: 8px !important; border: none !important;
    }
    div.stButton > button:hover { background-color: #1d4ed8 !important; }
</style>

""", unsafe_allow_html=True)

_usuario = st.session_state.get("usuario")
_nav_btn = f'<span class="navbar-login">{_usuario}</span>' if _usuario else '<a href="/login" class="navbar-login">Iniciar sesión</a>'

st.markdown(f"""
<div class="navbar">
    <div class="navbar-logo">Legion<span style="color:#3b82f6;">.</span>Flight</div>
    <div class="navbar-links">
        <a href="#buscar-vuelo">Buscar vuelo</a>
        <a href="#favoritos">Favoritos</a>
        <a href="#como-funciona">Cómo funciona</a>
        <a href="#contacto">Contacto</a>
    </div>
    <div class="navbar-right">{_nav_btn}</div>
</div>
""", unsafe_allow_html=True)

# --- HERO ---
img_path = os.path.join(current_dir, "assets", "avion.jpeg")

st.title("Descubre como sera tu vuelo")
st.write("Convierte la incertidumbre en información: conoce las condiciones meteorológicas en origen y destino antes de embarcar.")
col_img, col_widget = st.columns([3, 1])

with col_img:
    st.markdown('<div style="max-height:220px;overflow:hidden;border-radius:8px;">', unsafe_allow_html=True)
    st.image(img_path, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.caption(f"✈ Análisis meteorológico de vuelos · {hero_city} · Live")

with col_widget:
    with st.container(border=True):
        st.metric("Aeropuerto", hero_iata)
        st.metric("Temperatura", h_temp)
        st.metric("Viento", h_wind_speed)
        st.metric("Dirección", h_wind_dir)
        st.metric("Estado", h_precip_label)

st.divider()

# --- BUSCADOR ---
st.markdown('<div id="buscar-vuelo"></div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

ciudades = list(CIUDADES_IATA.keys())

with col1:
    origen = st.selectbox("Ciudad / Aeropuerto salida", options=ciudades, index=0)

with col2:
    destino = st.selectbox("Ciudad / Aeropuerto llegada", options=ciudades, index=1)

with col3:
    _today = _dt.date.today()
    _one_month = _today + _dt.timedelta(days=30)
    _min_date = max(available_dates[0], _today)
    _max_date = min(available_dates[-1], _one_month)
    # Si hoy no está en los datos disponibles, usar el primer disponible
    _default = _min_date if _min_date in available_dates else available_dates[0]
    fecha = st.date_input(
        "Fecha salida",
        value=_default,
        min_value=_min_date,
        max_value=_max_date,
    )

with col4:
    buscar = st.button("Buscar vuelos")
    ya_ruta_guardada = any(
        r["origen"] == origen and r["destino"] == destino
        for r in st.session_state["rutas_favoritas"]
    )
    label_ruta = "★ Ruta guardada" if ya_ruta_guardada else "☆ Guardar ruta"
    if st.button(label_ruta, key="guardar_ruta"):
        if not st.session_state.get("usuario"):
            st.toast("Inicia sesión para guardar rutas", icon="🔒")
        elif origen == destino:
            st.toast("Origen y destino no pueden ser iguales", icon="⚠️")
        elif ya_ruta_guardada:
            st.session_state["rutas_favoritas"] = [
                r for r in st.session_state["rutas_favoritas"]
                if not (r["origen"] == origen and r["destino"] == destino)
            ]
            usuarios = cargar_usuarios()
            u = st.session_state["usuario"]
            if u in usuarios:
                usuarios[u]["rutas_favoritas"] = st.session_state["rutas_favoritas"]
            guardar_usuarios(usuarios)
            st.toast("Ruta eliminada de favoritos", icon="🗑️")
            st.rerun()
        else:
            st.session_state["rutas_favoritas"].append({
                "origen": origen, "destino": destino,
                "iata_orig": CIUDADES_IATA[origen], "iata_dest": CIUDADES_IATA[destino],
            })
            usuarios = cargar_usuarios()
            u = st.session_state["usuario"]
            if u in usuarios:
                usuarios[u]["rutas_favoritas"] = st.session_state["rutas_favoritas"]
            guardar_usuarios(usuarios)
            st.toast("Ruta guardada en favoritos", icon="⭐")
            st.rerun()

# --- RESULTADOS ---
# Los resultados se almacenan en session_state para que persistan
# entre reruns, necesario para que los botones funcionen al hacer clic
if buscar:
    if origen == destino:
        st.error("El aeropuerto de origen y destino no pueden ser el mismo.")
        st.session_state.pop("resultados", None)
    else:
        vuelos_reales = buscar_programacion_comercial(origen, destino, str(fecha))
        if not vuelos_reales:
            st.warning("No se encontraron vuelos comerciales programados.")
            st.session_state.pop("resultados", None)
        else:
            vuelos_reales = sorted(vuelos_reales, key=lambda x: (x['hora_int'], x['minuto_int']))
            enriquecidos = []
            for vuelo in vuelos_reales:
                w_orig = get_weather_at(df_weather, origen, fecha, vuelo["hora_int"])
                w_dest = get_weather_at(df_weather, destino, fecha, (vuelo["hora_int"] + 1) % 24)
                if w_orig and w_dest:
                    datos_o = {
                        "temperature":    w_orig.get('temperature', 20),
                        "wind_speed":     w_orig.get('wind_speed', 0),
                        "precipitation":  w_orig.get('precipitation', 0),
                        "wind_direction": w_orig.get('wind_direction', 0),
                    }
                    datos_d = {
                        "temperature":    w_dest.get('temperature', 20),
                        "wind_speed":     w_dest.get('wind_speed', 0),
                        "precipitation":  w_dest.get('precipitation', 0),
                        "wind_direction": w_dest.get('wind_direction', 0),
                    }
                    result     = score_flight(datos_o, datos_d)
                    nota_final = result.get('rating', 0.0)
                    etiqueta   = result.get('label', 'Malo')
                    color_nota = result.get('color', '#dc3545')
                    precio = vuelo.get("precio")
                    enriquecidos.append({
                        "vuelo":       vuelo,
                        "datos_o":     datos_o,
                        "datos_d":     datos_d,
                        "nota_final":  nota_final,
                        "etiqueta":    etiqueta,
                        "color_nota":  color_nota,
                        "precio":      precio,
                        "origen":      origen,
                        "destino":     destino,
                        "fecha":       str(fecha),
                    })
            st.session_state["resultados"] = enriquecidos

# Renderizamos desde session_state para que los botones sigan funcionando tras rerun
for item in st.session_state.get("resultados", []):
    vuelo      = item["vuelo"]
    datos_o    = item["datos_o"]
    datos_d    = item["datos_d"]
    nota_final = item["nota_final"]
    etiqueta   = item["etiqueta"]
    color_nota = item["color_nota"]
    precio     = item["precio"]
    origen_r   = item["origen"]
    destino_r  = item["destino"]
    fecha_r    = item["fecha"]

    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([1, 2, 1, 1])
        with c1:
            st.markdown(f"### {vuelo['hora_salida']}")
            st.caption(vuelo['linea'])
            st.caption(vuelo['vuelo'])
        with c2:
            st.markdown(f"## {CIUDADES_IATA[origen_r]} → {CIUDADES_IATA[destino_r]}")
            st.caption("Con escala · Programado" if vuelo.get("escala") else "Directo · Programado")
        with c3:
            precio_str = f"{precio} €" if precio else "—"
            st.metric("Precio", precio_str)
            st.caption(f"{datos_o['temperature']}°C / {datos_d['temperature']}°C · {datos_o['wind_speed']} km/h")
        with c4:
            st.metric(etiqueta, f"{nota_final:.1f} / 10")

    btn_col1, btn_col2 = st.columns(2)

    with btn_col1:
        if st.button("Ver detalle", key=f"det_{vuelo['vuelo']}_{vuelo['hora_salida']}"):
            st.session_state["vuelo_seleccionado"] = {
                "linea":       vuelo["linea"],
                "vuelo":       vuelo["vuelo"],
                "hora_salida": vuelo["hora_salida"],
                "hora_int":    vuelo["hora_int"],
                "estado":      vuelo.get("estado", "N/A"),
                "origen":      origen_r,
                "destino":     destino_r,
                "iata_orig":   CIUDADES_IATA[origen_r],
                "iata_dest":   CIUDADES_IATA[destino_r],
                "fecha":       fecha_r,
                "temp_orig":   datos_o["temperature"],
                "viento_orig": datos_o["wind_speed"],
                "precip_orig": datos_o["precipitation"],
                "dir_orig":    datos_o["wind_direction"],
                "temp_dest":   datos_d["temperature"],
                "viento_dest": datos_d["wind_speed"],
                "precip_dest": datos_d["precipitation"],
                "dir_dest":    datos_d["wind_direction"],
                "nota":        nota_final,
                "etiqueta":    etiqueta,
                "color":       color_nota,
                "precio":      precio,
            }
            st.switch_page("pages/detalle_vuelo.py")

    with btn_col2:
        ya_guardado = any(
            f["vuelo"] == vuelo["vuelo"] and f["hora_salida"] == vuelo["hora_salida"]
            for f in st.session_state["favoritos"]
        )
        label_fav = "★ Guardado" if ya_guardado else "☆ Guardar"

        if st.button(label_fav, key=f"fav_{vuelo['vuelo']}_{vuelo['hora_salida']}"):
            if not st.session_state.get("usuario"):
                st.toast("Inicia sesión para guardar favoritos", icon="🔒")
            else:
                if ya_guardado:
                    st.session_state["favoritos"] = [
                        f for f in st.session_state["favoritos"]
                        if not (f["vuelo"] == vuelo["vuelo"] and f["hora_salida"] == vuelo["hora_salida"])
                    ]
                    st.toast("Eliminado de favoritos", icon="🗑️")
                else:
                    fav = {
                        "origen":      origen_r,
                        "destino":     destino_r,
                        "iata_orig":   CIUDADES_IATA[origen_r],
                        "iata_dest":   CIUDADES_IATA[destino_r],
                        "fecha":       fecha_r,
                        "hora_salida": vuelo["hora_salida"],
                        "linea":       vuelo["linea"],
                        "vuelo":       vuelo["vuelo"],
                        "nota":        nota_final,
                        "etiqueta":    etiqueta,
                        "color":       color_nota,
                        "temp_orig":   datos_o["temperature"],
                        "temp_dest":   datos_d["temperature"],
                        "viento":      datos_o["wind_speed"],
                        "precio":      precio,
                    }
                    st.session_state["favoritos"].append(fav)
                    st.toast("Vuelo guardado en favoritos", icon="⭐")

                usuarios = cargar_usuarios()
                username = st.session_state["usuario"]
                if username in usuarios:
                    usuarios[username]["favoritos"] = st.session_state["favoritos"]
                guardar_usuarios(usuarios)
                st.rerun()

# --- FAVORITOS ---
st.markdown('<div id="favoritos"></div>', unsafe_allow_html=True)
st.divider()
st.header("Vuelos favoritos")

if not st.session_state.get("usuario"):
    st.info("Inicia sesión para ver tus vuelos guardados")
    if st.button("Iniciar sesión", key="btn_login_favoritos"):
        st.switch_page("pages/login.py")
elif not st.session_state["favoritos"]:
    st.caption("Aún no tienes vuelos guardados.")
else:
    for fav in st.session_state["favoritos"]:
        precio_fav = fav.get("precio")
        precio_fav_str = f"{precio_fav} €" if precio_fav else "—"

        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([1, 2, 1, 1])
            with c1:
                st.markdown(f"### {fav['hora_salida']}")
                st.caption(fav['linea'])
                st.caption(f"{fav['vuelo']} · {fav['fecha']}")
            with c2:
                st.markdown(f"## {fav['iata_orig']} → {fav['iata_dest']}")
                st.caption(f"{fav['origen']} → {fav['destino']}")
            with c3:
                st.metric("Precio", precio_fav_str)
                st.caption(f"{fav['temp_orig']}°C / {fav['temp_dest']}°C · {fav['viento']} km/h")
            with c4:
                st.metric(fav['etiqueta'], f"{fav['nota']:.1f} / 10")

        fav_col1, fav_col2 = st.columns(2)
        with fav_col1:
            if st.button("Ver detalle", key=f"det_fav_{fav['vuelo']}_{fav['hora_salida']}"):
                st.session_state["vuelo_seleccionado"] = {
                    "linea":       fav["linea"],
                    "vuelo":       fav["vuelo"],
                    "hora_salida": fav["hora_salida"],
                    "hora_int":    int(fav["hora_salida"].split(":")[0]),
                    "estado":      "N/A",
                    "origen":      fav["origen"],
                    "destino":     fav["destino"],
                    "iata_orig":   fav["iata_orig"],
                    "iata_dest":   fav["iata_dest"],
                    "fecha":       fav["fecha"],
                    "temp_orig":   fav["temp_orig"],
                    "viento_orig": fav["viento"],
                    "precip_orig": 0,
                    "dir_orig":    0,
                    "temp_dest":   fav["temp_dest"],
                    "viento_dest": fav["viento"],
                    "precip_dest": 0,
                    "dir_dest":    0,
                    "nota":        fav["nota"],
                    "etiqueta":    fav["etiqueta"],
                    "color":       fav["color"],
                    "precio":      fav.get("precio", 0),
                }
                st.switch_page("pages/detalle_vuelo.py")
        with fav_col2:
            if st.button("Eliminar", key=f"del_{fav['vuelo']}_{fav['hora_salida']}"):
                st.session_state["favoritos"] = [
                    f for f in st.session_state["favoritos"]
                    if not (f["vuelo"] == fav["vuelo"] and f["hora_salida"] == fav["hora_salida"])
                ]
                usuarios = cargar_usuarios()
                username = st.session_state["usuario"]
                if username in usuarios:
                    usuarios[username]["favoritos"] = st.session_state["favoritos"]
                guardar_usuarios(usuarios)
                st.rerun()

# --- RUTAS FAVORITAS ---
st.divider()
st.header("Rutas favoritas")

if not st.session_state.get("usuario"):
    st.info("Inicia sesión para ver tus rutas guardadas")
elif not st.session_state["rutas_favoritas"]:
    st.caption("Aún no tienes rutas guardadas. Guarda una ruta desde el buscador.")
else:
    cols = st.columns(3)
    for i, ruta in enumerate(st.session_state["rutas_favoritas"]):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"### {ruta['iata_orig']} → {ruta['iata_dest']}")
                st.caption(f"{ruta['origen']} → {ruta['destino']}")
                bc1, bc2 = st.columns(2)
                if bc1.button("Buscar vuelos", key=f"buscar_ruta_{i}"):
                    st.session_state["_ruta_activa"] = i
                if bc2.button("Eliminar", key=f"del_ruta_{i}"):
                    st.session_state["rutas_favoritas"].pop(i)
                    st.session_state.pop("_ruta_activa", None)
                    usuarios = cargar_usuarios()
                    u = st.session_state["usuario"]
                    if u in usuarios:
                        usuarios[u]["rutas_favoritas"] = st.session_state["rutas_favoritas"]
                    guardar_usuarios(usuarios)
                    st.rerun()

    # Buscador inline para la ruta activa
    idx_activo = st.session_state.get("_ruta_activa")
    if idx_activo is not None and idx_activo < len(st.session_state["rutas_favoritas"]):
        ruta_a = st.session_state["rutas_favoritas"][idx_activo]
        st.divider()
        st.subheader(f"Vuelos: {ruta_a['iata_orig']} → {ruta_a['iata_dest']}")

        _today2   = _dt.date.today()
        _min2     = max(available_dates[0], _today2)
        _max2     = min(available_dates[-1], _today2 + _dt.timedelta(days=30))
        _default2 = _min2 if _min2 in available_dates else available_dates[0]
        fecha_ruta = st.date_input("Fecha", value=_default2, min_value=_min2, max_value=_max2, key="fecha_ruta_fav")

        vuelos_ruta = buscar_programacion_comercial(ruta_a["origen"], ruta_a["destino"], str(fecha_ruta))

        if not vuelos_ruta:
            st.warning("No se encontraron vuelos para esta ruta y fecha.")
        else:
            for vuelo in vuelos_ruta:
                w_orig = get_weather_at(df_weather, ruta_a["origen"], fecha_ruta, vuelo["hora_int"])
                w_dest = get_weather_at(df_weather, ruta_a["destino"], fecha_ruta, (vuelo["hora_int"] + 1) % 24)
                if not w_orig or not w_dest:
                    continue
                datos_o = {"temperature": w_orig.get("temperature", 20), "wind_speed": w_orig.get("wind_speed", 0),
                           "precipitation": w_orig.get("precipitation", 0), "wind_direction": w_orig.get("wind_direction", 0)}
                datos_d = {"temperature": w_dest.get("temperature", 20), "wind_speed": w_dest.get("wind_speed", 0),
                           "precipitation": w_dest.get("precipitation", 0), "wind_direction": w_dest.get("wind_direction", 0)}
                result = score_flight(datos_o, datos_d)
                nota_final = result.get("rating", 0.0)
                etiqueta   = result.get("label", "Malo")
                color_nota = result.get("color", "#dc3545")
                precio_r   = vuelo.get("precio")

                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([1, 2, 1, 1])
                    with c1:
                        st.markdown(f"### {vuelo['hora_salida']}")
                        st.caption(vuelo["linea"])
                        st.caption(vuelo["vuelo"])
                    with c2:
                        st.markdown(f"## {ruta_a['iata_orig']} → {ruta_a['iata_dest']}")
                        st.caption("Con escala · Programado" if vuelo.get("escala") else "Directo · Programado")
                    with c3:
                        st.metric("Precio", f"{precio_r} €" if precio_r else "—")
                        st.caption(f"{datos_o['temperature']}°C / {datos_d['temperature']}°C · {datos_o['wind_speed']} km/h")
                    with c4:
                        st.metric(etiqueta, f"{nota_final:.1f} / 10")

                if st.button("Ver detalle", key=f"det_rutafav_{vuelo['vuelo']}_{vuelo['hora_salida']}"):
                    st.session_state["vuelo_seleccionado"] = {
                        "linea": vuelo["linea"], "vuelo": vuelo["vuelo"],
                        "hora_salida": vuelo["hora_salida"], "hora_int": vuelo["hora_int"],
                        "estado": vuelo.get("estado", "scheduled"),
                        "origen": ruta_a["origen"], "destino": ruta_a["destino"],
                        "iata_orig": ruta_a["iata_orig"], "iata_dest": ruta_a["iata_dest"],
                        "fecha": str(fecha_ruta),
                        "temp_orig": datos_o["temperature"], "viento_orig": datos_o["wind_speed"],
                        "precip_orig": datos_o["precipitation"], "dir_orig": datos_o["wind_direction"],
                        "temp_dest": datos_d["temperature"], "viento_dest": datos_d["wind_speed"],
                        "precip_dest": datos_d["precipitation"], "dir_dest": datos_d["wind_direction"],
                        "nota": nota_final, "etiqueta": etiqueta, "color": color_nota,
                        "precio": precio_r,
                    }
                    st.switch_page("pages/detalle_vuelo.py")

# --- CÓMO FUNCIONA ---
st.markdown('<div id="como-funciona"></div>', unsafe_allow_html=True)
st.divider()
st.header("Cómo funciona")

col_a, col_b, col_c = st.columns(3)
with col_a:
    with st.container(border=True):
        st.subheader("1. Busca")
        st.write("Selecciona tu aeropuerto de origen, destino y fecha de vuelo.")
with col_b:
    with st.container(border=True):
        st.subheader("2. Analiza")
        st.write("Consulta las condiciones meteorológicas reales en origen y destino.")
with col_c:
    with st.container(border=True):
        st.subheader("3. Decide")
        st.write("Elige el horario con mejores condiciones para volar.")

# --- CONTACTO ---
st.markdown('<div id="contacto"></div>', unsafe_allow_html=True)
st.divider()
st.header("Contacto")
st.write("¿Tienes dudas? Escríbenos a **contacto@legionflight.com**")

# --- FAQ ---
st.divider()
st.header("FAQ")

faq_items = [
    ("¿De dónde salen los datos meteorológicos?", "Utilizamos Open-Meteo, un servicio meteorológico de código abierto que combina modelos numéricos de alta precisión como el European Centre for Medium-Range Weather Forecasts (ECMWF) y el Global Forecast System (GFS)."),
    ("¿Qué variables meteorológicas se analizan?", "Analizamos tres factores clave: temperatura, velocidad del viento y precipitación. Cada uno tiene un peso distinto en la puntuación final del vuelo."),
    ("¿Cómo se calcula la puntuación del vuelo?", "Utilizamos un algoritmo propio que combina distintas variables meteorológicas en origen y destino para generar una puntuación del 0 al 10. El resultado refleja las condiciones globales del trayecto."),
    ("¿Hasta cuándo puedo consultar previsiones?", "Cubrimos aproximadamente 30 días hacia adelante con datos reales."),
]

for pregunta, respuesta in faq_items:
    with st.expander(pregunta):
        st.write(respuesta)
