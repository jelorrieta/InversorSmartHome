# Imagen base oficial de Python
FROM python:3.13-slim

# Directorio de trabajo
WORKDIR /app

# Copiar código y dependencias
COPY main.py requirements.txt ./

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Puerto a exponer
ENV PORT 8080
EXPOSE 8080

# Comando para Gunicorn (multi-thread, 4 workers)
CMD exec gunicorn --bind :$PORT --workers 4 --threads 4 --timeout 300 main:app
