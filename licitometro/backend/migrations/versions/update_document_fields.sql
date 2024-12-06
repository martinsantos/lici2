-- Actualizar la longitud del campo url en la tabla documents
ALTER TABLE documents ALTER COLUMN url TYPE VARCHAR(255);
-- Actualizar la longitud del campo nombre en la tabla documents
ALTER TABLE documents ALTER COLUMN nombre TYPE VARCHAR(100);
-- Actualizar la longitud del campo tipo en la tabla documents
ALTER TABLE documents ALTER COLUMN tipo TYPE VARCHAR(100);
