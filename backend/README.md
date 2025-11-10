# Backend API - Tic-Tac-Toe

REST API built with FastAPI for the game.

## Quick start with Docker

```bash
# Start services
docker-compose up -d

# Check status
docker-compose ps
```

API will be at http://localhost:8000

Interactive documentation: http://localhost:8000/docs

Default user:
- Email: admin@tictactoe.com
- Password: changethis123

The admin user is created automatically when you start Docker.

## Local development

If you prefer to run without Docker:

```bash
cd backend

# Install uv
irm https://astral.sh/uv/install.ps1 | iex

# Install dependencies
uv sync

# Start only MariaDB
docker-compose up mariadb -d

# Run migrations
uv run alembic upgrade head

# Create superuser
uv run python app/initial_data.py

# Start development server
uv run fastapi dev app/main.py
```

## Endpoints

Authentication:
- POST /api/v1/signup - Register new user
- POST /api/v1/login/access-token - Login (returns JWT)
- POST /api/v1/login/test-token - Validate token

Users:
- GET /api/v1/users/ - List all (admin only)
- POST /api/v1/users/ - Create user (admin only)
- GET /api/v1/users/me - Current user
- PATCH /api/v1/users/me - Update profile
- GET /api/v1/users/{id} - Get specific user

Games:
- POST /api/v1/games/ - Create new game
- GET /api/v1/games/ - List my games
- GET /api/v1/games/{id} - View specific game
- POST /api/v1/games/{id}/move - Make a move

Health:
- GET /health - Service status

## Structure

```
app/
  api/
    routes/
      login.py      Authentication
      users.py      User management
      games.py      Game logic
  core/
    config.py       Environment variables
    db.py           Database connection
    security.py     JWT and passwords
    logger.py       Logging system
    game_engine.py  Game rules
  services/
    user_service.py     User logic
    game_service.py     Game logic
    ai_service.py       AI with OpenRouter
  models.py         Database models
  initial_data.py   Script to create admin
```

## Configuration

Create a `.env` file in the project root:

```env
ENVIRONMENT=local
PROJECT_NAME=Tic-Tac-Toe API
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=11520

MYSQL_SERVER=localhost
MYSQL_PORT=33060
MYSQL_USER=tictactoe_user
MYSQL_PASSWORD=tictactoe_pass
MYSQL_DB=tictactoe

FIRST_SUPERUSER=admin@tictactoe.com
FIRST_SUPERUSER_PASSWORD=changethis123

OPENROUTER_API_KEYS=your-api-keys-here
OPENROUTER_MODEL=openrouter/polaris-alpha

RATE_LIMIT_ENABLED=true
RATE_LIMIT_LOGIN=5/minute
RATE_LIMIT_SIGNUP=3/minute
```

## Migrations

Create new migration:
```bash
docker-compose exec backend alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
docker-compose exec backend alembic upgrade head
```

View history:
```bash
docker-compose exec backend alembic history
```

Revert:
```bash
docker-compose exec backend alembic downgrade -1
```

## Logs

The system saves logs to two files inside the `logs/` directory:

- app.log: All events (INFO, DEBUG, WARNING, ERROR)
- errors.log: Only errors

Files rotate when they reach 10MB, 5 versions are kept.

View logs in real time:
```bash
docker-compose exec backend tail -f logs/app.log
docker-compose exec backend tail -f logs/errors.log
```

Logged events:
- Successful and failed login attempts
- Game creation and updates
- Player moves and AI responses
- OpenRouter API calls
- Errors with stack traces

## Rate Limiting

The API includes request limiting:

- Login: 5 attempts per minute
- Signup: 3 attempts per minute
- AI moves: 30 per minute
- General: 100 requests per minute

If you hit the limit you'll receive a 429 error.

## Security

- Passwords hashed with bcrypt
- JWT tokens with expiration
- CORS configured
- Rate limiting enabled
- SQL injection prevented by SQLModel
- Input validation with Pydantic

## Common issues

Error "relation user does not exist":
```bash
docker-compose exec backend alembic upgrade head !!scripted via .sh using docker-compose!!
docker-compose exec backend python app/initial_data.py
```

See what's happening:
```bash
docker-compose logs -f backend
```

Restart services:
```bash
docker-compose restart
```

Start from scratch (deletes everything):
```bash
docker-compose down -v
docker-compose up -d
```
