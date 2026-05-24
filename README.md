# Legion Flight

🔗 **App desplegada:** [legion-flight.streamlit.app](https://legion-flight.streamlit.app)

Descubre cómo será tu vuelo antes de despegar. Consulta las condiciones meteorológicas en origen y destino, puntuación del trayecto y precios reales.

## Integrantes

Neide Ochocho Penet · Guillermo Diaz Barrero · Mateo Molina Garibo · Rodrigo Gutman Nieto Peret

## Estructura

```
src/        pipeline de datos (descarga, limpieza, scoring, APIs)
web/        app Streamlit (app.py + pages/)
data/       datos generados en ejecución (ignorados por git)
```

## Variables de entorno

Crea un archivo `.env` en la raíz del proyecto con:

```
SERPAPI_KEY=tu_clave_aqui
```

La clave se obtiene en [serpapi.com](https://serpapi.com).

---

## Ejecución manual

### 1. Entorno virtual e instalación

```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### 2. Descargar datos meteorológicos

```bash
python src/download.py
```

Descarga datos históricos (últimos 7 días) y previsión (30 días) para todos los aeropuertos desde Open-Meteo. Guarda el resultado en `data/raw/weather_data.json`.

### 3. Limpiar y convertir a CSV

```bash
python src/clean.py
```

Convierte `data/raw/weather_data.json` a `data/clean/weather_data.csv`.

### 4. Arrancar la app

```bash
streamlit run web/app.py
```
---

## Ejecución con Docker

La aplicación se divide en dos contenedores que se ejecutan en orden:

```
APIs externas → [data-pipeline] → volumen /data → [streamlit-app] → Usuario
```

- **data-pipeline**: ejecuta `download.py` y `clean.py`, escribe los datos en el volumen compartido y se apaga.
- **streamlit-app**: arranca después del pipeline, lee los datos del volumen y sirve la app en el puerto 8501.

```bash
docker compose up --build
```

Para forzar una actualización de datos sin reconstruir las imágenes:

```bash
docker compose up
```
