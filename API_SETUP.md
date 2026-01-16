# Akitoi API - Setup Guide

Esta guía te ayudará a configurar y desplegar la API de Akitoi.

## 🚀 Inicio Rápido

### 1. Instalar Dependencias

```bash
# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -e .
```

### 2. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus valores
nano .env
```

### 3. Inicializar Base de Datos (Opcional - para PostgreSQL)

```bash
# Crear migración inicial
./scripts/init_db.sh
```

### 4. Ejecutar en Desarrollo

```bash
# Opción 1: Usar el script
./scripts/run_dev.sh

# Opción 2: Comando directo
uvicorn src.akitoi.api.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en:
- **API**: http://localhost:8000
- **Documentación interactiva**: http://localhost:8000/docs
- **Documentación alternativa**: http://localhost:8000/redoc

## 📡 Endpoints Disponibles

### Health Check
- `GET /health` - Verificar estado de la API

### Profiles
- `GET /api/v1/profiles` - Listar todos los perfiles
- `GET /api/v1/profiles/{slug}` - Obtener perfil por slug
- `POST /api/v1/profiles` - Crear nuevo perfil
- `PATCH /api/v1/profiles/{profile_id}` - Actualizar perfil
- `DELETE /api/v1/profiles/{profile_id}` - Eliminar perfil
- `POST /api/v1/profiles/{profile_id}/links` - Agregar link a perfil
- `POST /api/v1/profiles/{profile_id}/publish` - Publicar perfil
- `POST /api/v1/profiles/{slug}/view` - Registrar vista

## 🧪 Ejemplos de Uso

### Crear un Perfil

```bash
curl -X POST "http://localhost:8000/api/v1/profiles" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Juan Tello",
    "slug": "juan-tello",
    "bio": "Tech entrepreneur & developer",
    "profile_image_url": "https://example.com/photo.jpg",
    "theme": {
      "primary_color": "#007bff",
      "background_color": "#ffffff",
      "text_color": "#333333"
    }
  }'
```

### Obtener Perfil por Slug

```bash
curl "http://localhost:8000/api/v1/profiles/juan-tello"
```

### Agregar Link a Perfil

```bash
curl -X POST "http://localhost:8000/api/v1/profiles/{profile_id}/links" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "whatsapp",
    "url": "https://wa.me/1234567890",
    "label": "WhatsApp",
    "icon": "whatsapp"
  }'
```

## 🌐 Deployment

### Opción 1: Render.com (Recomendado para empezar)

1. **Crear cuenta en Render.com**: https://render.com

2. **Conectar tu repositorio de GitHub**

3. **Crear Web Service**:
   - Build Command: `pip install -e .`
   - Start Command: `uvicorn src.akitoi.api.main:app --host 0.0.0.0 --port $PORT`

4. **Crear PostgreSQL Database**:
   - Plan: Free
   - Database Name: akitoi

5. **Configurar Variables de Entorno**:
   - `DATABASE_URL`: (Auto-configurado desde database)
   - `ENVIRONMENT`: `production`

6. **Deploy**: Render automáticamente desplegará usando `render.yaml`

### Opción 2: Fly.io (Más flexible)

```bash
# Instalar CLI de Fly.io
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Crear app
flyctl launch

# Agregar PostgreSQL
flyctl postgres create

# Conectar database
flyctl postgres attach <postgres-app-name>

# Deploy
flyctl deploy
```

### Opción 3: Vercel (Solo para frontend - requiere Next.js)

Vercel es ideal para el frontend de Next.js, no para la API de FastAPI.
Para el backend, usa Render.com o Fly.io.

## 🗄️ Base de Datos

### Opción 1: Supabase (Recomendado para producción)

**Supabase** es la opción recomendada para producción. Ofrece:
- PostgreSQL completo con 500MB gratis
- Dashboard intuitivo para gestionar datos
- APIs REST y GraphQL automáticas
- Storage para imágenes de perfil y logos
- Authentication integrada

**Configuración completa**: Ver [SUPABASE_SETUP.md](./SUPABASE_SETUP.md)

**Setup rápido**:

1. Crear proyecto en [supabase.com](https://supabase.com)
2. Obtener credenciales en Project Settings > Database
3. Configurar `.env`:

```env
DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

4. Inicializar base de datos:

```bash
./scripts/init_db.sh
```

5. Verificar:

```bash
python3 scripts/check_db.py
```

### Opción 2: JSON Storage (Para desarrollo local)

La aplicación puede usar `JSONStorage` por defecto, guardando datos en `.akitoi_data/`.

No requiere configuración adicional, útil para desarrollo rápido.

### Opción 3: PostgreSQL Local (Para desarrollo)

1. **Instalar PostgreSQL localmente**

2. **Crear base de datos**:
```bash
createdb akitoi
```

3. **Configurar DATABASE_URL** en `.env`:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/akitoi
```

4. **Ejecutar migraciones**:
```bash
./scripts/init_db.sh
```

## 🔧 Comandos Útiles

```bash
# Ver logs de la API
uvicorn src.akitoi.api.main:app --reload --log-level debug

# Crear nueva migración
alembic revision --autogenerate -m "descripción"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1

# Ver historial de migraciones
alembic history

# Formatear código
black src/ tests/
ruff check --fix src/ tests/

# Ejecutar tests
pytest
```

## 📊 Estructura del Proyecto

```
akitoi/
├── src/akitoi/
│   ├── api/              # FastAPI application
│   │   ├── main.py       # App principal
│   │   └── routes/       # Endpoints
│   ├── database/         # SQLAlchemy models
│   │   ├── connection.py # DB connection
│   │   └── models.py     # DB models
│   ├── core/             # Business logic
│   ├── models/           # Pydantic models
│   └── storage/          # Storage backends
├── alembic/              # Database migrations
├── scripts/              # Utility scripts
├── tests/                # Tests
├── .env.example          # Environment variables template
├── render.yaml           # Render.com config
├── fly.toml              # Fly.io config
└── Procfile              # Process file
```

## 🔐 Seguridad

Para producción, asegúrate de:

1. Configurar `ALLOWED_ORIGINS` en `.env` con tus dominios
2. Usar HTTPS
3. Implementar autenticación (JWT, OAuth)
4. Limitar rate limiting
5. Sanitizar inputs

## 📝 Próximos Pasos

- [ ] Implementar autenticación con JWT
- [ ] Agregar rate limiting
- [ ] Implementar caché con Redis
- [ ] Agregar tests de integración
- [ ] Configurar CI/CD
- [ ] Agregar logging avanzado
- [ ] Implementar WebSockets para analytics en tiempo real

## 🆘 Troubleshooting

### Error: "ModuleNotFoundError"
```bash
pip install -e .
```

### Error: "Could not connect to database"
Verifica que PostgreSQL esté corriendo y que `DATABASE_URL` sea correcta.

### Error: "Port already in use"
```bash
# Cambiar puerto
uvicorn src.akitoi.api.main:app --port 8001
```

## 📚 Recursos

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org)
- [Alembic Documentation](https://alembic.sqlalchemy.org)
- [Render Documentation](https://render.com/docs)
- [Fly.io Documentation](https://fly.io/docs)
