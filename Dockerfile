# Usa imagen base oficial de Python
FROM python:3.13-slim

# Directorio de trabajo
WORKDIR /app

# Copia archivos
COPY main.py requirements.txt ./

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Puerto que Cloud Run expone
ENV PORT 8080

# Comando para ejecutar la app con gunicorn
# -w 1: un worker
# -b 0.0.0.0:$PORT: escucha en el puerto que Cloud Run asigna
CMD ["gunicorn", "-w", "1", "--threads", "4", "--timeout", "120", "-b", "0.0.0.0:8080", "main:app"]
