#!/bin/bash
# Startup script for Railway backend

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
