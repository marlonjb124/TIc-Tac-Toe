# Backend API - Tic-Tac-Toe

FastAPI REST API with JWT authentication and AI integration.

## Quick Start

```bash
# From project root
docker-compose up -d
```

API: http://localhost:8000
Docs: http://localhost:8000/api/v1/docs

Default admin: admin@tictactoe.com / changethis123

## Local Development

```bash
cd backend
irm https://astral.sh/uv/install.ps1 | iex  # Install uv
uv sync
docker-compose up mariadb -d
uv run alembic upgrade head
uv run python app/initial_data.py
uv run fastapi dev app/main.py
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/signup` - Register user
- `POST /api/v1/auth/login/access-token` - Login
- `POST /api/v1/auth/login/test-token` - Validate token

### Users
- `GET /api/v1/users/me` - Get current user
- `GET /api/v1/users/me/stats` - Get game stats
- `PATCH /api/v1/users/me` - Update profile

### Games
- `POST /api/v1/games/` - Create game
- `GET /api/v1/games/` - List games (query: `?status=in_progress`)
- `GET /api/v1/games/{id}` - Get game
- `POST /api/v1/games/{id}/move` - Make move

Interactive docs: http://localhost:8000/api/v1/docs

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── routes/       # login.py, users.py, games.py
│   │   └── deps.py       # Auth dependencies
│   ├── core/
│   │   ├── config.py     # Settings
│   │   ├── db.py         # Database
│   │   ├── security.py   # JWT & passwords
│   │   └── logger.py     # Logging
│   ├── services/         # Business logic
│   ├── models.py         # Database models
│   └── main.py           # FastAPI app
├── logs/                 # Auto-created
└── alembic/              # Migrations
```

## Configuration

Edit `.env` file in project root:

```env
# Database (use 'mariadb' when in Docker, 'localhost' when local)
MYSQL_SERVER=localhost
MYSQL_PORT=33060
MYSQL_USER=tictactoe_user
MYSQL_PASSWORD=tictactoe_pass
MYSQL_DB=tictactoe

# Security
SECRET_KEY=changethis-in-production
FIRST_SUPERUSER=admin@tictactoe.com
FIRST_SUPERUSER_PASSWORD=changethis123

# OpenRouter
OPENROUTER_API_KEYS=sk-or-v1-xxxxx
OPENROUTER_MODEL=openrouter/polaris-alpha
```

## Database Migrations

```bash
# Create migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec backend alembic upgrade head

# View history
docker-compose exec backend alembic history

# Rollback
docker-compose exec backend alembic downgrade -1
```

## Logging

Logs in `backend/logs/`:
- `app.log` - All events
- `errors.log` - Errors only

```bash
# View logs
docker-compose exec backend tail -f /app/logs/app.log
docker-compose exec backend tail -f /app/logs/errors.log
```

Files rotate at 10MB, 5 backups kept.

## Security

- Password hashing with bcrypt
- JWT authentication
- Rate limiting (login: 5/min, signup: 3/min)
- CORS enabled for frontend
- Input validation with Pydantic

## Troubleshooting

**Database errors:**
```bash
docker-compose exec backend alembic upgrade head
docker-compose exec backend python app/initial_data.py
```

**Can't connect to MariaDB:**
```bash
docker-compose ps mariadb
docker-compose logs mariadb
docker-compose restart mariadb
```

**Backend keeps restarting:**
```bash
docker-compose logs backend
docker-compose up -d --build backend
```

**Fresh start:**
```bash
docker-compose down -v
docker-compose up -d
```
