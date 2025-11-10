# Frontend - Tic-Tac-Toe

React + TypeScript frontend with Tailwind CSS.

## Quick Start

```bash
cd frontend
pnpm install
pnpm run dev
```

App runs at http://localhost:5173

## Build

```bash
pnpm run build      # Production build
pnpm run preview    # Preview build
```

## Project Structure

```
frontend/
├── src/
│   ├── components/         # Board, Cell, ProtectedRoute
│   ├── pages/              # Login, Signup, Dashboard, Game
│   ├── hooks/              # useApi (TanStack Query)
│   ├── api/                # Axios client
│   └── types/              # TypeScript types
├── public/
└── vite.config.ts
```

## Features

**Pages:**
- Login / Signup
- Dashboard (stats, game history)
- Game board

**Tech Stack:**
- React 18
- TypeScript
- Vite
- Tailwind CSS v4
- TanStack Query
- React Router

## Troubleshooting

**Network errors:**
- Check backend is running: `curl http://localhost:8000/health`
- Verify API URL in `src/api/index.ts`

**Styles not loading:**
```bash
rm -rf node_modules/.vite
pnpm run dev
```

**TypeScript errors:**
- Check types match backend schemas in `src/types/index.ts`
