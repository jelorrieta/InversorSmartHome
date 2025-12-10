# Imagen base oficial de Python
FROM python:3.13-slim

# Directorio de trabajo
WORKDIR /app

# Copia archivos
COPY main.py requirements.txt ./

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Puerto que Cloud Run expone
ENV PORT 8080

# Comando para ejecutar la app con gunicorn (1 worker, hilos, timeout extendido)
CMD ["gunicorn", "-w", "1", "-k", "gthread", "-t", "300", "-b", "0.0.0.0:8080", "main:app"]
