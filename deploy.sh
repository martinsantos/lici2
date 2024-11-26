#!/bin/bash

# Cargar variables de entorno
export DB_PASSWORD=$(openssl rand -hex 16)

# Construir imágenes
docker-compose build

# Iniciar servicios
docker-compose up -d

# Mostrar estado de los servicios
docker-compose ps

# Mostrar logs
docker-compose logs -f
