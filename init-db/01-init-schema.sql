-- Crear esquema base
CREATE SCHEMA IF NOT EXISTS licitometro;

-- Establecer ruta de búsqueda
SET search_path TO licitometro;

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla de Licitaciones
CREATE TABLE IF NOT EXISTS licitaciones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    published_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    closing_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50),
    category VARCHAR(100),
    budget NUMERIC(15,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Modelos de Machine Learning
CREATE TABLE IF NOT EXISTS ml_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    type VARCHAR(100),
    accuracy NUMERIC(5,2),
    training_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Predicciones
CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID REFERENCES ml_models(id),
    input_data JSONB,
    output_data JSONB,
    confidence NUMERIC(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Usuarios
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    role VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_licitaciones_status ON licitaciones(status);
CREATE INDEX IF NOT EXISTS idx_licitaciones_category ON licitaciones(category);
CREATE INDEX IF NOT EXISTS idx_ml_models_name ON ml_models(name);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Datos de ejemplo
INSERT INTO licitaciones (title, description, status, category, budget) 
VALUES 
    ('Licitación de Infraestructura', 'Proyecto de modernización de infraestructura', 'ABIERTA', 'INFRAESTRUCTURA', 1000000.00),
    ('Licitación de Tecnología', 'Adquisición de equipos tecnológicos', 'CERRADA', 'TECNOLOGÍA', 500000.00)
ON CONFLICT DO NOTHING;

-- Crear usuario para la aplicación
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'licitometro_app') THEN
        CREATE ROLE licitometro_app WITH LOGIN PASSWORD 'licitometro_app_secret';
    END IF;
END
$$;

-- Otorgar permisos
GRANT USAGE ON SCHEMA licitometro TO licitometro_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA licitometro TO licitometro_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA licitometro TO licitometro_app;
