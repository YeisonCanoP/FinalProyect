FROM python:3.12-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app

# Instalar dependencias de Chrome y del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget gnupg ca-certificates curl unzip fontconfig \
    libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 \
    libxi6 libxtst6 libnss3 libglib2.0-0 libxrandr2 libasound2 libatk1.0-0 libgtk-3-0 \
    fonts-liberation xdg-utils libu2f-udev \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && ln -s /usr/bin/google-chrome /usr/bin/chrome \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt ./
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el resto de archivos
COPY . .

# Copiar y dar permisos al script de inicio
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Exponer puertos
EXPOSE 8000
EXPOSE 52928

# Comando de arranque
CMD ["/start.sh"]
