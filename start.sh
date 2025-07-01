#!/bin/sh

# Ejecutar FastAPI en segundo plano
uvicorn app.services.cognitoapi:app --host 0.0.0.0 --port 8000 &

# Ejecutar Flet en modo web
python app/main.py
