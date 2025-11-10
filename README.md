# Tic-Tac-Toe with AI

Tic-tac-toe game against an AI that uses OpenRouter. FastAPI backend with MariaDB, React frontend.

## First time setup

You need to have installed:
- Docker and Docker Compose
- Node.js 18 or higher
- pnpm (install with `npm install -g pnpm`)

### Steps

1. Clone the repo and navigate to the directory:
```bash
git clone https://github.com/marlonjb124/TIc-Tac-Toe.git
cd TIc-Tac-Toe
```

2. Create a `.env` file in the root with your OpenRouter API key:
```env
OPENROUTER_API_KEYS=your-keys-here
```

Get one for free at openrouter.ai if you don't have one. Note: free keys have usage limits.

3. Start the backend and database:
```bash
docker-compose up -d
```

This will:
- Create the MariaDB database
- Run migrations automatically
- Create the admin user (admin@tictactoe.com / changethis123)
- Start the API on port 8000

4. Install and start the frontend:
```bash
cd frontend
pnpm install
pnpm run dev
```

The game will be at http://localhost:5173

The API has interactive documentation at http://localhost:8000/api/v1/docs

## Project structure

```
backend/
  app/
    api/          REST endpoints
    core/         Configuration, security, logging
    services/     Game and AI logic
    scripts/      Migrate and seed
    models.py     Database models
  logs/           Created automatically
  Dockerfile

frontend/
  src/
    components/   React components
    pages/        Main pages
    hooks/        Custom hooks
    types/        TypeScript types

docker-compose.yml  Backend + MariaDB
```

## Useful commands

Check what's running:
```bash
docker-compose ps
```

View backend logs:
```bash
docker-compose logs -f backend
```

View application logs (inside container):
```bash
docker-compose exec backend tail -f logs/app.log
```

Restart everything:
```bash
docker-compose restart
```

Start from scratch (deletes DB):
```bash
docker-compose down -v
docker-compose up -d
```

## Local backend development

If you prefer to run the backend without Docker:

```bash
cd backend

# Install uv if you don't have it
irm https://astral.sh/uv/install.ps1 | iex

# Install dependencies
uv sync

# Start only MariaDB
docker-compose up mariadb -d

# Run migrations
uv run alembic upgrade head

# Create superuser
uv run python app/initial_data.py

# Start server
uv run fastapi dev app/main.py
```

## Technologies

Backend:
- FastAPI for the API
- SQLModel as ORM
- MariaDB for data
- OpenRouter (polaris-alpha model) for AI
- SlowAPI for rate limiting

Frontend:
- React 18 with TypeScript
- Vite as bundler
- Tailwind CSS v4
- TanStack Query for state management
- Axios for requests

## How the AI works

The AI analyzes the board before each move:
1. Check if it can win this turn
2. If not, block if player can win
3. If not, choose center or corners based on strategy
4. Adjust intelligence based on chosen difficulty

Levels:
- Easy: Random play, blocks obvious wins 50% of the time
- Medium: Always blocks and takes wins, basic strategy
- Hard: Perfect play, thinks several moves ahead

## Logging system

The backend saves logs to two files:
- `logs/app.log`: Everything (info, debug, warnings, errors)
- `logs/errors.log`: Only errors

Files rotate automatically when they reach 10MB, 5 versions are kept.

Logged events:
- Successful and failed logins
- Game creation
- Player and AI moves
- OpenRouter API calls
- Errors with complete stack traces

## Common issues

Frontend won't connect:
- Verify backend is running with `docker-compose ps`
- Check logs with `docker-compose logs backend`

Can't login:
- Admin user is created automatically when starting Docker
- Wait a few seconds for it to finish initializing
- User: admin@tictactoe.com
- Password: changethis123

AI doesn't respond:
- Check that OpenRouter API key is correct in .env
- Look at logs: `docker-compose logs -f backend`
- Verify you have credits in your OpenRouter account

Migration errors:
```bash
docker-compose down -v
docker-compose up -d
```

## License

MIT

## Author

Marlon Jiménez - github.com/marlonjb124
