# Tic-Tac-Toe API Backend

API REST construida con FastAPI para el juego de Tic-Tac-Toe.

## Inicio Rápido

### Con Docker (recomendado)

```bash
# Iniciar servicios
docker-compose up -d

# Primera vez: ejecutar migraciones y crear usuario admin
docker-compose exec backend alembic upgrade head
docker-compose exec backend python app/initial_data.py

# Verificar
docker-compose ps
```

Acceder a la documentación: http://localhost:8000/api/v1/docs

**Credenciales de prueba:**
- Email: admin@tictactoe.com
- Password: changethis123

### Desarrollo local

```bash
cd backend

# Instalar uv (si no lo tienes)
irm https://astral.sh/uv/install.ps1 | iex

# Instalar dependencias
uv sync

# Iniciar solo la base de datos
docker-compose up mariadb -d

# Ejecutar migraciones
uv run alembic upgrade head

# Crear superusuario
uv run python app/initial_data.py

# Iniciar servidor
uv run fastapi dev app/main.py
```

## Endpoints principales

### Autenticación
- `POST /api/v1/login/access-token` - Obtener token JWT
- `POST /api/v1/login/test-token` - Validar token

### Usuarios
- `GET /api/v1/users/` - Listar usuarios (solo admin)
- `POST /api/v1/users/` - Crear usuario
- `GET /api/v1/users/{id}` - Obtener usuario
- `GET /api/v1/users/me` - Usuario actual
- `PATCH /api/v1/users/me` - Actualizar usuario actual

### Health
- `GET /health` - Estado del servicio

## Arquitectura

```
app/
ENVIRONMENT=local
PROJECT_NAME=Tic-Tac-Toe API
SECRET_KEY=changethis
ACCESS_TOKEN_EXPIRE_MINUTES=11520

MYSQL_SERVER=localhost
MYSQL_PORT=33060
MYSQL_USER=tictactoe_user
MYSQL_PASSWORD=tictactoe_pass
MYSQL_DB=tictactoe

FIRST_SUPERUSER=admin@tictactoe.com
FIRST_SUPERUSER_PASSWORD=changethis123
```

## Troubleshooting

**Error "relation user does not exist"**
```bash
docker-compose exec backend alembic upgrade head
docker-compose exec backend python app/initial_data.py
```

**Ver logs**
```bash
docker-compose logs -f backend
```

**Reiniciar**
```bash
docker-compose restart
```

**Recrear BD**
```bash
docker-compose down -v
docker-compose up -d
```
