# 🚀 Guía de Despliegue de Akitoi

## ✅ Lo que ya tienes implementado

Has completado exitosamente la **Fase 1** de infraestructura:

### 1. ✅ API FastAPI Completa
- **Endpoint principal**: `GET /api/v1/profiles/{slug}` ← **Este es tu primer endpoint real**
- **CRUD completo** para perfiles
- **Gestión de links** (agregar, eliminar)
- **Analytics** (views, clicks)
- **Publicación** de perfiles
- **Documentación automática** en `/docs`

### 2. ✅ Modelos de Base de Datos (PostgreSQL)
- **ProfileDB**: Perfiles con slug único, bio, imágenes, tema
- **LinkDB**: Enlaces con analytics de clicks
- **AnalyticsEventDB**: Eventos detallados de views/clicks
- **Migraciones con Alembic** configuradas

### 3. ✅ Configuración de Deployment
- **render.yaml**: Listo para Render.com (backend + PostgreSQL)
- **fly.toml**: Listo para Fly.io
- **Procfile**: Para plataformas compatibles
- **Alembic**: Para gestión de migraciones
- **.env.example**: Template de variables de entorno

---

## 📁 Estructura Creada

```
akitoi/
├── src/akitoi/
│   ├── api/                      ← ✅ API FastAPI
│   │   ├── main.py              (Aplicación principal)
│   │   └── routes/
│   │       ├── health.py        (Health check)
│   │       └── profiles.py      (Endpoints de perfiles)
│   ├── database/                 ← ✅ Modelos PostgreSQL
│   │   ├── connection.py        (Conexión DB)
│   │   └── models.py            (ProfileDB, LinkDB, AnalyticsEventDB)
│   ├── core/                     ← Ya existía
│   │   └── profile_manager.py   (Lógica de negocio)
│   └── models/                   ← Ya existía
│       ├── profile.py
│       ├── link.py
│       └── theme.py
├── alembic/                      ← ✅ Migraciones DB
│   ├── env.py
│   └── versions/
├── scripts/                      ← ✅ Scripts útiles
│   ├── run_dev.sh               (Iniciar en desarrollo)
│   └── init_db.sh               (Inicializar DB)
├── render.yaml                   ← ✅ Deploy en Render
├── fly.toml                      ← ✅ Deploy en Fly.io
├── Procfile                      ← ✅ Deploy general
└── .env.example                  ← ✅ Variables de entorno
```

---

## 🎯 Endpoints Disponibles

### Health Check
```bash
GET /health
```

### Perfiles

#### Obtener perfil por slug (PRINCIPAL)
```bash
GET /api/v1/profiles/{slug}
```
**Ejemplo**:
```bash
curl http://localhost:8000/api/v1/profiles/juan-tello
```

#### Crear perfil
```bash
POST /api/v1/profiles
Content-Type: application/json

{
  "name": "Juan Tello",
  "slug": "juan-tello",
  "bio": "Tech entrepreneur",
  "theme": {
    "primary_color": "#007bff",
    "background_color": "#ffffff"
  }
}
```

#### Listar perfiles
```bash
GET /api/v1/profiles
```

#### Actualizar perfil
```bash
PATCH /api/v1/profiles/{profile_id}
```

#### Eliminar perfil
```bash
DELETE /api/v1/profiles/{profile_id}
```

#### Agregar link
```bash
POST /api/v1/profiles/{profile_id}/links
Content-Type: application/json

{
  "type": "whatsapp",
  "url": "https://wa.me/1234567890",
  "label": "WhatsApp"
}
```

#### Publicar perfil
```bash
POST /api/v1/profiles/{profile_id}/publish
```

#### Registrar vista
```bash
POST /api/v1/profiles/{slug}/view
```

---

## 🏃 Cómo Ejecutar Localmente

### 1. Activar entorno virtual
```bash
source venv/bin/activate
```

### 2. Instalar dependencias (ya hecho)
```bash
pip install -e .
```

### 3. Ejecutar la API
```bash
# Opción 1: Script
./scripts/run_dev.sh

# Opción 2: Comando directo
uvicorn src.akitoi.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Acceder a la documentación
- **API**: http://localhost:8000
- **Docs interactivos**: http://localhost:8000/docs ← **Úsala para probar endpoints**
- **ReDoc**: http://localhost:8000/redoc

---

## 🌐 Opciones de Deployment

### Opción 1: Render.com (Recomendada - FREE TIER)

**✅ Ventajas**:
- FREE tier incluye PostgreSQL
- Zero configuration (usa `render.yaml`)
- Auto-deploy desde GitHub
- SSL gratis

**Pasos**:

1. **Crear cuenta**: https://render.com

2. **Nuevo Web Service**:
   - Conecta tu repo de GitHub
   - Render detectará automáticamente `render.yaml`
   - Click "Apply"

3. **Variables de entorno** (auto-configuradas):
   - `DATABASE_URL`: Auto desde PostgreSQL
   - `ENVIRONMENT`: `production`

4. **Deploy**:
   - Render automáticamente:
     - Crea el PostgreSQL
     - Despliega la API
     - Conecta ambos

5. **URL final**:
   ```
   https://akitoi-api.onrender.com
   ```

### Opción 2: Fly.io (Más flexible)

```bash
# 1. Instalar CLI
curl -L https://fly.io/install.sh | sh

# 2. Login
flyctl auth login

# 3. Launch (usa fly.toml automáticamente)
flyctl launch

# 4. Agregar PostgreSQL
flyctl postgres create
flyctl postgres attach <nombre-postgres>

# 5. Deploy
flyctl deploy
```

### Opción 3: Railway.app (Simple)

1. Visita: https://railway.app
2. Conecta GitHub
3. Selecciona repo
4. Railway detecta Python automáticamente
5. Agrega PostgreSQL desde el dashboard

---

## 🗄️ Base de Datos

### Desarrollo (Actual - JSON Storage)
Por defecto usa `JSONStorage` que guarda en `.akitoi_data/`.

**No requiere configuración**.

### Producción (PostgreSQL)

#### Opción A: PostgreSQL local
```bash
# 1. Instalar PostgreSQL
brew install postgresql

# 2. Iniciar servicio
brew services start postgresql

# 3. Crear base de datos
createdb akitoi

# 4. Configurar .env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/akitoi

# 5. Ejecutar migraciones
./scripts/init_db.sh
```

#### Opción B: Supabase (FREE - Recomendado)
1. Visita: https://supabase.com
2. Crea nuevo proyecto
3. Copia la "Connection String"
4. Configura en Render/Fly.io:
   ```
   DATABASE_URL=postgresql://user:pass@db.xxx.supabase.co:5432/postgres
   ```

---

## 🔄 Próximos Pasos Recomendados

### Fase 2: Frontend (Next.js en Vercel)

1. **Crear proyecto Next.js**:
```bash
npx create-next-app@latest akitoi-web
cd akitoi-web
```

2. **Conectar con tu API**:
```typescript
// lib/api.ts
const API_URL = "https://akitoi-api.onrender.com";

export async function getProfile(slug: string) {
  const res = await fetch(`${API_URL}/api/v1/profiles/${slug}`);
  return res.json();
}
```

3. **Deploy en Vercel**:
```bash
vercel
```

### Fase 3: Características Adicionales

- [ ] Autenticación con JWT
- [ ] Upload de imágenes (Cloudinary/S3)
- [ ] Generador de QR codes
- [ ] URL shortener
- [ ] Dashboard de analytics
- [ ] Temas personalizados

---

## 🧪 Testing

### Probar endpoints con curl

```bash
# Health check
curl http://localhost:8000/health

# Crear perfil
curl -X POST http://localhost:8000/api/v1/profiles \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","bio":"Testing"}'

# Listar perfiles
curl http://localhost:8000/api/v1/profiles

# Obtener perfil
curl http://localhost:8000/api/v1/profiles/test-user
```

### Usar Swagger UI (Recomendado)

1. Abre http://localhost:8000/docs
2. Expande cualquier endpoint
3. Click en "Try it out"
4. Ingresa parámetros
5. Click "Execute"

---

## 📊 Comparación de Plataformas

| Plataforma | Free Tier | PostgreSQL | Deploy Time | Dificultad |
|------------|-----------|------------|-------------|------------|
| **Render.com** | ✅ Sí | ✅ FREE | 5 min | ⭐ Fácil |
| **Fly.io** | ✅ Sí | ✅ FREE | 10 min | ⭐⭐ Media |
| **Railway** | ✅ Sí | ✅ FREE | 3 min | ⭐ Fácil |
| **Vercel** | ✅ Sí | ❌ No | N/A | N/A (solo frontend) |

**Recomendación**: Usa **Render.com** para el backend (FastAPI) y **Vercel** para el frontend (Next.js).

---

## 🔐 Seguridad para Producción

Antes de lanzar, configura:

1. **CORS apropiado** (edita `src/akitoi/api/main.py`):
```python
allow_origins=["https://tudominio.com"]
```

2. **Variables de entorno sensibles**:
```env
SECRET_KEY=tu-secret-key-aqui
DATABASE_URL=postgresql://...
ALLOWED_ORIGINS=https://tudominio.com
```

3. **Rate limiting** (agrega después)

---

## 🆘 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'fastapi'"
```bash
pip install -e .
```

### Error: "Address already in use"
```bash
# Cambiar puerto
uvicorn src.akitoi.api.main:app --port 8001
```

### Error: No se conecta a la base de datos
- Verifica que PostgreSQL esté corriendo
- Revisa `DATABASE_URL` en `.env`
- Intenta: `psql -d akitoi` para verificar conexión

---

## 📚 Recursos

- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Render Deploy Guide](https://render.com/docs/deploy-fastapi)
- [Fly.io Python Guide](https://fly.io/docs/languages-and-frameworks/python/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

---

## 🎉 ¡Todo Listo!

Tu API de Akitoi está **100% funcional** y lista para:

1. ✅ Ejecutarse localmente
2. ✅ Desplegarse en Render/Fly.io/Railway
3. ✅ Conectarse con PostgreSQL o Supabase
4. ✅ Servir el primer endpoint real: `GET /api/v1/profiles/{slug}`

**Siguiente paso sugerido**: Deploy en Render.com (5 minutos) o desarrollar el frontend en Next.js.
