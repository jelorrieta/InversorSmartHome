# Usa imagen base oficial de Python
FROM python:3.13-slim

# Directorio de trabajo
WORKDIR /app

# Copia archivos
COPY main.py requirements.txt ./

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt gunicorn flask

# Puerto que Cloud Run expone
ENV PORT 8080

# Comando para ejecutar la app con gunicorn
# -w 1: 1 worker (puede aumentar si necesitas más concurrencia)
# -b 0.0.0.0:$PORT: escuchar en el puerto asignado por Cloud Run
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8080", "main:app"]
