#!/bin/bash

# Script de inicio para servicios del módulo RECON

# Cargar variables de entorno
source .env

# Función para manejar errores
handle_error() {
    echo "Error: $1"
    exit 1
}

# Iniciar Redis
start_redis() {
    echo "Iniciando Redis..."
    redis-server &
    REDIS_PID=$!
    sleep 2
    if ! kill -0 $REDIS_PID 2>/dev/null; then
        handle_error "No se pudo iniciar Redis"
    fi
}

# Iniciar Celery Worker
start_celery_worker() {
    echo "Iniciando Celery Worker..."
    celery -A backend.recon.celery_worker.celery_app worker --loglevel=INFO &
    CELERY_WORKER_PID=$!
    sleep 2
    if ! kill -0 $CELERY_WORKER_PID 2>/dev/null; then
        handle_error "No se pudo iniciar Celery Worker"
    fi
}

# Iniciar Celery Beat (tareas programadas)
start_celery_beat() {
    echo "Iniciando Celery Beat..."
    celery -A backend.recon.celery_worker.celery_app beat --loglevel=INFO &
    CELERY_BEAT_PID=$!
    sleep 2
    if ! kill -0 $CELERY_BEAT_PID 2>/dev/null; then
        handle_error "No se pudo iniciar Celery Beat"
    fi
}

# Iniciar Flower (monitoreo de tareas)
start_flower() {
    echo "Iniciando Flower..."
    flower --port=$FLOWER_PORT &
    FLOWER_PID=$!
    sleep 2
    if ! kill -0 $FLOWER_PID 2>/dev/null; then
        handle_error "No se pudo iniciar Flower"
    fi
}

# Iniciar servicio FastAPI
start_fastapi() {
    echo "Iniciando servicio FastAPI RECON..."
    uvicorn backend.recon.main:app --host $RECON_API_HOST --port $RECON_API_PORT --reload &
    FASTAPI_PID=$!
    sleep 2
    if ! kill -0 $FASTAPI_PID 2>/dev/null; then
        handle_error "No se pudo iniciar servicio FastAPI"
    fi
}

# Función principal de inicio
main() {
    start_redis
    start_celery_worker
    start_celery_beat
    start_flower
    start_fastapi

    echo "Todos los servicios del módulo RECON han sido iniciados."
    echo "Redis en $REDIS_HOST:$REDIS_PORT"
    echo "Celery Worker activo"
    echo "Celery Beat programado"
    echo "Flower en http://localhost:$FLOWER_PORT"
    echo "FastAPI RECON en http://$RECON_API_HOST:$RECON_API_PORT"

    # Esperar a que los procesos terminen
    wait
}

# Función de limpieza al salir
cleanup() {
    echo "Deteniendo servicios..."
    kill $REDIS_PID $CELERY_WORKER_PID $CELERY_BEAT_PID $FLOWER_PID $FASTAPI_PID 2>/dev/null
    exit 0
}

# Capturar señales de terminación
trap cleanup SIGINT SIGTERM

# Ejecutar función principal
main
