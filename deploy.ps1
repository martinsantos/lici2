# Generar contraseña aleatoria
$env:DB_PASSWORD = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 16 | ForEach-Object {[char]$_})

# Construir imágenes
docker-compose build

# Iniciar servicios
docker-compose up -d

# Mostrar estado de los servicios
docker-compose ps

# Mostrar logs
docker-compose logs -f
