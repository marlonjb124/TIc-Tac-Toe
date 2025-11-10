# Tic-Tac-Toe Game with AI

Un juego de Tic-Tac-Toe (tres en raya) con IA basada en OpenRouter, construido con FastAPI, React y MariaDB.

## 🚀 Inicio Rápido

### Prerequisitos
- **Docker y Docker Compose** (para backend y base de datos)
- **Node.js 18+** (para el frontend)
- **pnpm** - Instalar con: `npm install -g pnpm`
- **API key de OpenRouter** - Obtén una gratis en [openrouter.ai](https://openrouter.ai)

### Instalación

1. **Clona el repositorio**
```bash
git clone https://github.com/marlonjb124/TIc-Tac-Toe.git
cd TIc-Tac-Toe
```

2. **Configura tu API key de OpenRouter**
   
   Crea/edita el archivo `.env` en la raíz del proyecto:
```env
OPENROUTER_API_KEYS=tu-api-key-aqui
```

3. **Inicia el backend y base de datos con Docker**
```bash
# Inicia MariaDB y el backend (automáticamente ejecuta migraciones y crea el superuser)
docker-compose up -d
```

4. **Inicia el frontend localmente**
```bash
cd frontend
pnpm install
pnpm run dev
```

¡Listo! La aplicación estará disponible en:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Usuario por defecto (creado automáticamente)
- **Email**: `admin@tictactoe.com`
- **Password**: `changethis123`

## 🎮 Características

- ✅ **Tres niveles de dificultad**: Fácil, Medio y Difícil
- ✅ **IA inteligente**: Potenciada por OpenRouter con análisis de amenazas
- ✅ **Interfaz moderna**: Diseño glassmorphism con animaciones
- ✅ **Autenticación JWT**: Sistema seguro de usuarios
- ✅ **Historial completo**: Revisa todas tus partidas anteriores

## 🛠️ Tecnologías

**Backend:**
- FastAPI (Python)
- SQLModel (ORM async)
- MariaDB 10.11
- OpenRouter AI (modelo: polaris-alpha)
- Docker

**Frontend:**
- React 18 + TypeScript
- Vite 7
- Tailwind CSS v4
- TanStack Query (React Query)
- Axios

## � Arquitectura del Proyecto

```
.
├── backend/              # API FastAPI
│   ├── app/
│   │   ├── api/         # Endpoints y rutas
│   │   ├── core/        # Configuración y seguridad
│   │   ├── models.py    # Modelos de base de datos
│   │   ├── services/    # Lógica de negocio (AI, juegos)
│   │   └── schemas/     # Schemas Pydantic
│   └── Dockerfile
├── frontend/            # App React
│   ├── src/
│   │   ├── components/  # Componentes reutilizables
│   │   ├── pages/       # Páginas principales
│   │   ├── hooks/       # Custom hooks (useApi)
│   │   └── types/       # TypeScript types
│   └── package.json
└── docker-compose.yml   # Orquestación Docker (backend + DB)
```

## �📝 Comandos útiles

### Docker

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs solo del backend
docker-compose logs -f backend

# Detener contenedores
docker-compose down

# Reiniciar desde cero (⚠️ elimina la base de datos)
docker-compose down -v
docker-compose up -d
# Las migraciones y el superuser se crean automáticamente

# Verificar estado de contenedores
docker-compose ps
```

### Frontend

```bash
# Instalar dependencias
cd frontend
pnpm install

# Modo desarrollo
pnpm run dev

# Build para producción
pnpm run build

# Preview del build
pnpm run preview
```

## 🔧 Desarrollo Avanzado

### Backend sin Docker

Si prefieres ejecutar el backend localmente sin Docker:

```bash
cd backend

# Crear entorno virtual con uv
uv venv
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate     # Windows

# Instalar dependencias
uv pip install -e .

# Configurar .env con tu base de datos local
# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
```

### Migraciones de Base de Datos

```bash
# Crear nueva migración
docker-compose exec backend alembic revision --autogenerate -m "descripcion"

# Aplicar migraciones
docker-compose exec backend alembic upgrade head

# Revertir última migración
docker-compose exec backend alembic downgrade -1

# Ver historial
docker-compose exec backend alembic history
```

## 🎯 Cómo Jugar

1. **Regístrate o inicia sesión** con el usuario por defecto
2. **Haz clic en "Nuevo Juego"**
3. **Selecciona la dificultad**:
   - 🟢 **Fácil**: La IA juega de forma aleatoria
   - 🟡 **Medio**: La IA bloquea tus jugadas ganadoras
   - 🔴 **Difícil**: La IA juega estratégicamente para ganar
4. **¡Juega!** - Tú eres las X, la IA son las O
5. **Revisa el historial** de todas tus partidas

## 🤖 Sobre la IA

La IA utiliza el modelo **Polaris Alpha** de OpenRouter con:
- Análisis de amenazas inmediatas (ganar/bloquear)
- Estrategia posicional (centro, esquinas, bordes)
- Ajuste de dificultad según selección del usuario
- Respuestas instantáneas con validación previa
cd frontend
## 🐛 Troubleshooting

### El frontend no se conecta al backend
- Verifica que el backend esté corriendo: `docker-compose ps`
- Revisa que el puerto 8000 esté disponible
- Asegúrate de que `.env` tenga tu API key de OpenRouter

### Error en migraciones de base de datos
```bash
# Reiniciar base de datos limpia (migraciones se ejecutan automáticamente)
docker-compose down -v
docker-compose up -d
```

### No puedo iniciar sesión
- El superuser se crea automáticamente al iniciar Docker
- Espera unos segundos a que el backend termine de inicializar
- Verifica los logs: `docker-compose logs backend`
- Credenciales: `admin@tictactoe.com` / `changethis123`

### La IA no responde
- Verifica que tu API key de OpenRouter sea válida
- Revisa los logs: `docker-compose logs -f backend`
- El modelo usado es `openrouter/polaris-alpha`

## 📄 Licencia

MIT

## 👨‍💻 Autor

Marlon Jiménez - [@marlonjb124](https://github.com/marlonjb124)
