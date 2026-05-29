FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Dejamos el contenedor abierto para ejecutar los scripts manualmente
CMD ["tail", "-f", "/dev/null"]
