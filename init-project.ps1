# Configurar ejecución estricta
$ErrorActionPreference = 'Stop'

# Verificar requisitos previos
if (!(Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Error "npm no está instalado. Por favor, instálelo e intente nuevamente."
    exit 1
}

if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker no está instalado. Por favor, instálelo e intente nuevamente."
    exit 1
}

# Instalar dependencias
npm install

# Generar cliente de Prisma
npm run prepare

# Crear red de Docker si no existe
docker network create licitometro-network 2>$null

# Iniciar base de datos en segundo plano
docker-compose up -d database

# Esperar a que la base de datos esté lista
Start-Sleep -Seconds 10

# Ejecutar migraciones
npm run migrate

# Sembrar datos iniciales
npm run seed

# Iniciar servicios restantes
docker-compose up -d

Write-Host "Proyecto Licitometro inicializado exitosamente" -ForegroundColor Green
