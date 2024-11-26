#!/bin/bash

# Detener la ejecución en caso de error
set -e

# Imprimir cada comando antes de ejecutarlo
set -x

# Verificar requisitos previos
command -v npm >/dev/null 2>&1 || { echo >&2 "npm es requerido pero no está instalado. Abortando."; exit 1; }
command -v docker >/dev/null 2>&1 || { echo >&2 "docker es requerido pero no está instalado. Abortando."; exit 1; }

# Instalar dependencias
npm install

# Generar cliente de Prisma
npm run prepare

# Crear red de Docker si no existe
docker network create licitometro-network 2>/dev/null || true

# Iniciar base de datos en segundo plano
docker-compose up -d database

# Esperar a que la base de datos esté lista (ajustar tiempo si es necesario)
sleep 10

# Ejecutar migraciones
npm run migrate

# Sembrar datos iniciales
npm run seed

# Iniciar servicios restantes
docker-compose up -d

echo "Proyecto Licitometro inicializado exitosamente"
