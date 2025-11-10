# Tic-Tac-Toe with AI

A tic-tac-toe game with an AI opponent powered by OpenRouter. Built with FastAPI backend and React frontend.

## Prerequisites

- Docker Desktop
- Node.js 18 or higher
- pnpm (`npm install -g pnpm`)

## Quick Start

**1. Clone the repository**
```bash
git clone https://github.com/marlonjb124/TIc-Tac-Toe.git
cd TIc-Tac-Toe
```

**2. Get OpenRouter API key**

Sign up at [openrouter.ai](https://openrouter.ai/) and create an API key.

**3. Create `.env` file**

Create a `.env` file in the project root:

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
**Note:** If you have multiple API keys, separate them with commas:
```env
OPENROUTER_API_KEYS=sk-or-v1-key1,sk-or-v1-key2,sk-or-v1-key3
```

**4. Create frontend `.env` file**

Create a `.env` file in the `frontend/` directory:
```bash
cd frontend
```

Create `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
```

**5. Start the backend**
```bash
docker-compose up -d
```

Wait about 30 seconds for initialization to complete.

**6. Start the frontend**
```bash
cd frontend
pnpm install
pnpm run dev
```

**7. Open the app**

Go to http://localhost:5173

Login with:
- Email: `admin@tictactoe.com`
- Password: `changethis123`

## Project Structure

```
backend/          FastAPI application
  app/
    api/          REST endpoints
    core/         Configuration and database
    services/     Business logic (AI, games, users)
    models.py     Database models
  logs/           Application logs

frontend/         React application
  src/
    components/   UI components
    pages/        Login, Dashboard, Game
    hooks/        API integration
    api/          HTTP client
```

## Common Commands

```bash
# Check status
docker-compose ps

# View logs
docker-compose logs -f backend

# Restart services
docker-compose restart

# Stop everything
docker-compose down

# Fresh start (deletes database)
docker-compose down -v
docker-compose up -d
```

## Development

To run the backend locally without Docker:

```bash
cd backend
irm https://astral.sh/uv/install.ps1 | iex  # Install uv
uv sync
docker-compose up mariadb -d
uv run alembic upgrade head
uv run python app/initial_data.py
uv run fastapi dev app/main.py
```

## Technologies

Backend: FastAPI, SQLModel, MariaDB, OpenRouter API
Frontend: React, TypeScript, Vite, Tailwind CSS, TanStack Query

## AI Difficulty Levels

- **Easy:** Random moves
- **Medium:** 70% chance to block/win, 30% random
- **Hard:** Always blocks and wins when possible

## Logging

Logs are saved in `backend/logs/`:
- `app.log` - All events
- `errors.log` - Errors only

View logs:
```bash
docker-compose exec backend tail -f /app/logs/app.log
```

## Troubleshooting

**Frontend won't connect**
- Check backend is running: `docker-compose ps`
- View logs: `docker-compose logs backend`

**Can't login**
- Wait 30 seconds after first startup
- Default credentials: admin@tictactoe.com / changethis123

**AI doesn't respond**
- Verify OpenRouter API key in `.env`
- Check you have credits at openrouter.ai
- View logs: `docker-compose logs backend`

**Database errors**
```bash
docker-compose exec backend alembic upgrade head
docker-compose exec backend python app/initial_data.py
```

## API Documentation

Interactive docs: http://localhost:8000/api/v1/docs

## License

MIT

## Author

Marlon Jiménez - [github.com/marlonjb124](https://github.com/marlonjb124)
