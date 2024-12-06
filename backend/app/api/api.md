# API Documentation

## Authentication

### POST /api/v1/token

Obtener token de acceso JWT mediante credenciales de usuario.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

**Status Codes:**
- 200: Token generado exitosamente
- 401: Credenciales inválidas

## Users

### POST /api/v1/users

Crear nuevo usuario en el sistema.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "string",
  "password": "string",
  "full_name": "string",
  "role": "user"
}
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "string",
  "full_name": "string",
  "role": "user",
  "is_active": true,
  "created_at": "datetime"
}
```

**Status Codes:**
- 201: Usuario creado exitosamente
- 400: Datos inválidos
- 409: Email o username ya existe

### GET /api/v1/users

Listar usuarios del sistema.

**Query Parameters:**
- skip (int): Número de registros a saltar
- limit (int): Límite de registros a retornar
- role (string): Filtrar por rol
- search (string): Búsqueda por nombre o email

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "username": "string",
      "full_name": "string",
      "role": "user",
      "is_active": true,
      "created_at": "datetime"
    }
  ],
  "total": 0
}
```

## Tenders

### POST /api/v1/tenders

Crear nueva licitación.

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "budget": 0,
  "start_date": "date",
  "end_date": "date",
  "status": "draft",
  "requirements": [
    {
      "title": "string",
      "description": "string",
      "is_mandatory": true
    }
  ],
  "documents": [
    {
      "title": "string",
      "url": "string",
      "type": "string"
    }
  ]
}
```

**Response:**
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "budget": 0,
  "start_date": "date",
  "end_date": "date",
  "status": "draft",
  "requirements": [],
  "documents": [],
  "created_by": "uuid",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### GET /api/v1/tenders

Listar licitaciones.

**Query Parameters:**
- skip (int): Número de registros a saltar
- limit (int): Límite de registros a retornar
- status (string): Filtrar por estado
- start_date (date): Filtrar por fecha inicio
- end_date (date): Filtrar por fecha fin
- search (string): Búsqueda por título o descripción

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "string",
      "description": "string",
      "budget": 0,
      "start_date": "date",
      "end_date": "date",
      "status": "string",
      "requirements_count": 0,
      "documents_count": 0,
      "created_at": "datetime"
    }
  ],
  "total": 0
}
```

### PATCH /api/v1/tenders/{id}/status

Actualizar estado de una licitación.

**Path Parameters:**
- id (uuid): ID de la licitación

**Request Body:**
```json
{
  "status": "string",
  "reason": "string"
}
```

**Response:**
```json
{
  "id": "uuid",
  "status": "string",
  "updated_at": "datetime"
}
```

## Error Responses

Todas las endpoints pueden retornar los siguientes errores:

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Item not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["string"],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```
