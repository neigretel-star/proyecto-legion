# Dockerfile.app - proyecto-legion
# Contenedor 2: sirve la app de Streamlit

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el codigo de la app y los modulos de src
# Los datos llegan a traves del volumen compartido
COPY src/ ./src/
COPY web/ ./web/

EXPOSE 8501

CMD ["streamlit", "run", "web/app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0"]
