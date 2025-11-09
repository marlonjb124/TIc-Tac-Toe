# Tic-Tac-Toe API Backend

API REST con FastAPI para gestión de usuarios y autenticación.

## Inicio Rápido

### Con Docker

```bash
docker-compose up -d

# Primera vez: configurar base de datos
docker-compose exec backend alembic upgrade head
docker-compose exec backend python app/initial_data.py
```

Documentación: http://localhost:8000/api/v1/docs

Credenciales:
- Email: admin@tictactoe.com
- Password: changethis123

### Desarrollo Local

```bash
cd backend
uv sync
docker-compose up mariadb -d
uv run alembic upgrade head
uv run python app/initial_data.py
uv run fastapi dev app/main.py
```

## Endpoints

**Autenticación**
- `POST /api/v1/login/access-token` - Login JWT
- `POST /api/v1/login/test-token` - Validar token

**Usuarios**
- `GET /api/v1/users/` - Listar usuarios (admin)
- `POST /api/v1/users/` - Crear usuario
- `GET /api/v1/users/{id}` - Usuario por ID
- `GET /api/v1/users/me` - Usuario actual
- `PATCH /api/v1/users/me` - Actualizar perfil

## Arquitectura

```
app/
├── api/routes/      # Endpoints HTTP
├── services/        # Lógica de negocio
├── core/            # Config, seguridad
├── models.py        # Modelos SQLModel
└── alembic/         # Migraciones
```

Patrón: Clean Architecture (API → Services → Models)

## Stack

- FastAPI - Framework web
- SQLModel - ORM
- Alembic - Migraciones
- MariaDB - Base de datos
- JWT + bcrypt - Autenticación


## Variables de Entorno

Crear `.env` en la raíz:

```env
ENVIRONMENT=local
SECRET_KEY=changethis-with-a-secure-random-key
MYSQL_SERVER=localhost
MYSQL_PORT=33060
MYSQL_USER=tictactoe_user
MYSQL_PASSWORD=tictactoe_pass
MYSQL_DB=tictactoe
FIRST_SUPERUSER=admin@tictactoe.com
FIRST_SUPERUSER_PASSWORD=changethis123
```

## Troubleshooting

**Error "relation 'user' does not exist"**
```bash
docker-compose exec backend alembic upgrade head
docker-compose exec backend python app/initial_data.py
```

**Ver logs**
```bash
docker-compose logs -f backend
```

**Recrear BD**
```bash
docker-compose down -v
docker-compose up -d
```
