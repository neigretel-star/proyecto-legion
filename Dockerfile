# Dockerfile - proyecto-legion
# Contenedor 1: descarga y limpia los datos

# Usamos la imagen oficial de Python 3.12 (slim es la version mas ligera)
FROM python:3.13-slim

# Esto evita que Python cree archivos .pyc y que los logs salgan en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Aqui le decimos al contenedor que trabaje dentro de la carpeta /app
WORKDIR /app

# Instalamos dependencias del sistema que algunas librerias de Python necesitan
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiamos el requirements.txt e instalamos las librerias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos solo el codigo del pipeline, no los datos
# Los datos se generan en ejecucion y se guardan en el volumen compartido
COPY src/ ./src/

# Descarga y limpia los datos, los deja en /app/data para el otro contenedor
CMD ["sh", "-c", "python src/download.py && python src/clean.py"]
