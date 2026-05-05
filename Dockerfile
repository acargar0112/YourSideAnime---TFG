# Imagen base de Python 3.12
FROM python:3.12-slim

# Evita que Python genere archivos .pyc (bytecode compilado) | Imagen limpia / Evita problemas de caché
ENV PYTHONDONTWRITEBYTECODE=1

# Hace que Python muestre logs directamente
ENV PYTHONUNBUFFERED=1

# Instala dependencias del sistema necesarias para compilar paquetes
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de dependencias
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Arranca Gunicorn sirviendo la aplicación Django
CMD ["gunicorn", "YourSideAnime.wsgi:application", "--bind", "0.0.0.0:8000"]
