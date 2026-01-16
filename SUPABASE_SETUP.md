# Configuración de Supabase para Akitoi

Esta guía te ayudará a configurar Supabase como base de datos para tu proyecto Akitoi.

## 📋 Tabla de Contenidos

1. [¿Por qué Supabase?](#por-qué-supabase)
2. [Crear Proyecto en Supabase](#crear-proyecto-en-supabase)
3. [Configurar Variables de Entorno](#configurar-variables-de-entorno)
4. [Inicializar Base de Datos](#inicializar-base-de-datos)
5. [Verificar Configuración](#verificar-configuración)
6. [Operaciones Comunes](#operaciones-comunes)
7. [Troubleshooting](#troubleshooting)

---

## ¿Por qué Supabase?

**Supabase** es una alternativa open-source a Firebase que ofrece:

- ✅ **PostgreSQL completo** - Base de datos relacional robusta
- ✅ **Tier gratuito generoso** - 500MB storage, 2GB bandwidth
- ✅ **APIs automáticas** - REST y GraphQL generadas automáticamente
- ✅ **Realtime subscriptions** - Para analytics en tiempo real
- ✅ **Autenticación integrada** - OAuth, email/password, magic links
- ✅ **Storage de archivos** - Para logos e imágenes de perfil
- ✅ **Dashboard intuitivo** - Para explorar datos y ejecutar queries

---

## Crear Proyecto en Supabase

### Paso 1: Crear Cuenta

1. Ve a [supabase.com](https://supabase.com)
2. Click en "Start your project"
3. Regístrate con GitHub, Google, o email

### Paso 2: Crear Nuevo Proyecto

1. En el dashboard, click en "New Project"
2. Completa los datos:
   - **Name**: `akitoi-production` (o el nombre que prefieras)
   - **Database Password**: Genera una contraseña segura (guárdala!)
   - **Region**: Elige la región más cercana a tus usuarios
   - **Pricing Plan**: Free (para empezar)

3. Click en "Create new project"
4. Espera 2-3 minutos mientras Supabase provisiona tu base de datos

### Paso 3: Obtener Credenciales

Una vez creado el proyecto, ve a **Project Settings** > **Database**:

#### Connection String (para Alembic y SQLAlchemy)

```
postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-ID].supabase.co:5432/postgres
```

Reemplaza:
- `[YOUR-PASSWORD]`: La contraseña que configuraste
- `[YOUR-PROJECT-ID]`: El ID único de tu proyecto

#### API Keys

Ve a **Project Settings** > **API**:

- **URL**: `https://[YOUR-PROJECT-ID].supabase.co`
- **anon public**: La API key pública (segura para cliente)
- **service_role**: La API key privada (solo para servidor)

---

## Configurar Variables de Entorno

### 1. Crear archivo .env

```bash
cp .env.example .env
```

### 2. Editar .env con tus credenciales

```bash
nano .env
```

### 3. Configurar variables de Supabase

```env
# ============================================
# Supabase Database Configuration
# ============================================
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Direct database connection (for Alembic migrations)
DATABASE_URL=postgresql://postgres:your-password@db.your-project-id.supabase.co:5432/postgres

# ============================================
# API Configuration
# ============================================
ENVIRONMENT=production
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# ============================================
# Security
# ============================================
SECRET_KEY=generate-a-secure-random-key-here
```

### 4. Generar SECRET_KEY

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copia el resultado y úsalo como `SECRET_KEY`.

---

## Inicializar Base de Datos

### Opción 1: Script Automático (Recomendado)

```bash
./scripts/init_db.sh
```

Este script:
1. ✅ Verifica la conexión a Supabase
2. ✅ Ejecuta las migraciones de Alembic
3. ✅ Crea todas las tablas e índices
4. ✅ Configura triggers automáticos

### Opción 2: Manual

```bash
# Verificar que Alembic puede conectarse
alembic current

# Ejecutar migraciones
alembic upgrade head

# Verificar estado
python3 scripts/check_db.py
```

---

## Verificar Configuración

### 1. Verificar con Script de Diagnóstico

```bash
python3 scripts/check_db.py
```

Deberías ver:
```
============================================================
Akitoi - Supabase Database Status Check
============================================================

🔗 Database URL: postgresql://postgres:****@db.xxx.supabase.co:5432/postgres

🔌 Testing database connection...
✅ Connected to PostgreSQL
   Version: PostgreSQL 15.x

📊 Checking database schema...

   Found 3 tables:
   ✅ profiles
   ✅ links
   ✅ analytics_events

📋 Table Details:
[... detalles de tablas ...]

✅ Database check complete!
```

### 2. Verificar en Dashboard de Supabase

1. Ve a tu proyecto en Supabase
2. Click en "Table Editor"
3. Deberías ver las tablas:
   - `profiles`
   - `links`
   - `analytics_events`
   - `alembic_version`

### 3. Ejecutar Query de Prueba

En el "SQL Editor" de Supabase:

```sql
-- Verificar estructura de tabla profiles
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'profiles'
ORDER BY ordinal_position;
```

---

## Operaciones Comunes

### Crear Nueva Migración

Cuando modifiques los modelos en `src/akitoi/database/models.py`:

```bash
# Generar migración automática
alembic revision --autogenerate -m "Descripción del cambio"

# Revisar el archivo generado en alembic/versions/

# Aplicar migración
alembic upgrade head
```

### Revertir Migración

```bash
# Revertir última migración
alembic downgrade -1

# Revertir a revisión específica
alembic downgrade <revision_id>

# Revertir todas las migraciones
alembic downgrade base
```

### Ver Historial de Migraciones

```bash
alembic history --verbose
```

### Consultar Datos Directamente

Usando Python:

```python
from src.akitoi.database.connection import SessionLocal
from src.akitoi.database.models import ProfileDB

db = SessionLocal()
profiles = db.query(ProfileDB).all()
for profile in profiles:
    print(f"{profile.slug}: {profile.name}")
db.close()
```

### Backup de Base de Datos

Desde el Dashboard de Supabase:
1. Ve a **Database** > **Backups**
2. Los backups automáticos se hacen diariamente
3. Puedes hacer backup manual con el botón "Back up now"

O por CLI:

```bash
# Instalar pg_dump (si no lo tienes)
brew install postgresql  # macOS
sudo apt install postgresql-client  # Ubuntu

# Hacer backup
pg_dump "postgresql://postgres:[PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres" > backup.sql

# Restaurar backup
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres" < backup.sql
```

---

## Esquema de Base de Datos

### Tabla: profiles

Almacena los perfiles de usuario/empresa.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | String(36) | UUID único del perfil |
| name | String(100) | Nombre del usuario/empresa |
| slug | String(50) | URL-friendly identifier (único) |
| bio | Text | Biografía/descripción |
| profile_image_url | String(500) | URL de foto de perfil |
| logo_url | String(500) | URL del logo |
| theme | JSONB | Configuración de tema (colores, fuente) |
| is_published | Boolean | Si el perfil está público |
| view_count | Integer | Contador de visitas |
| created_at | Timestamp | Fecha de creación |
| updated_at | Timestamp | Fecha de última actualización |

**Índices:**
- `slug` (UNIQUE)
- `is_published, created_at` (compuesto)
- `view_count`

### Tabla: links

Almacena los enlaces de contacto/redes sociales.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | String(36) | UUID único del link |
| profile_id | String(36) | FK a profiles.id |
| type | String(50) | Tipo de link (email, whatsapp, etc.) |
| url | String(500) | URL del link |
| label | String(100) | Etiqueta personalizada |
| icon | String(100) | Nombre del icono |
| order | Integer | Orden de visualización |
| click_count | Integer | Contador de clicks |
| created_at | Timestamp | Fecha de creación |

**Índices:**
- `profile_id, order` (compuesto)
- `profile_id, type` (compuesto)

### Tabla: analytics_events

Almacena eventos de analíticas (vistas, clicks).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | ID autoincrementable |
| profile_id | String(36) | FK a profiles.id |
| link_id | String(36) | FK a links.id (nullable) |
| event_type | String(50) | Tipo de evento (view, click) |
| metadata | JSONB | Metadata adicional (referrer, etc.) |
| created_at | Timestamp | Fecha del evento |

**Índices:**
- `profile_id, created_at` (compuesto)
- `event_type, created_at` (compuesto)
- `link_id`

---

## Troubleshooting

### Error: "could not connect to server"

**Problema**: No se puede conectar a Supabase.

**Soluciones**:
1. Verifica que el `DATABASE_URL` sea correcto
2. Verifica que la contraseña no tenga caracteres especiales sin escapar
3. Verifica que tu IP no esté bloqueada (en Settings > Database > Connection Pooling)
4. Verifica que el proyecto de Supabase esté activo

### Error: "password authentication failed"

**Problema**: La contraseña es incorrecta.

**Soluciones**:
1. Ve a Supabase Dashboard > Settings > Database
2. Click en "Reset Database Password"
3. Actualiza tu `.env` con la nueva contraseña

### Error: "SSL connection required"

**Problema**: Supabase requiere SSL.

**Solución**: Agrega `?sslmode=require` al final de tu `DATABASE_URL`:

```env
DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres?sslmode=require
```

### Error: "prepared statement already exists"

**Problema**: Conflicto con connection pooling de Supabase.

**Solución**: Ya está manejado en `src/akitoi/database/connection.py` con `NullPool`.

### Rendimiento Lento

**Problema**: Las queries son lentas.

**Soluciones**:
1. Verifica que los índices estén creados: `python3 scripts/check_db.py`
2. Usa el "Query Performance" tool en Supabase Dashboard
3. Considera agregar índices adicionales según tus queries más frecuentes
4. Usa connection pooling (PgBouncer está habilitado por defecto)

### Límites del Tier Gratuito

**Límites del plan gratuito**:
- 500 MB de almacenamiento
- 2 GB de transferencia mensual
- 2 proyectos
- Pausa automática después de 1 semana de inactividad

**Si llegas al límite**:
1. Limpia eventos antiguos: usa `cleanup_old_analytics()` en `utils.py`
2. Considera upgrade a plan Pro ($25/mes)
3. Usa múltiples proyectos para desarrollo/staging/producción

---

## Recursos Adicionales

- [Documentación de Supabase](https://supabase.com/docs)
- [Supabase CLI](https://supabase.com/docs/guides/cli)
- [SQLAlchemy con PostgreSQL](https://docs.sqlalchemy.org/en/14/dialects/postgresql.html)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [PostgreSQL Performance Tips](https://wiki.postgresql.org/wiki/Performance_Optimization)

---

## Próximos Pasos

Ahora que tienes Supabase configurado:

1. ✅ **Ejecutar la API**: `./scripts/run_dev.sh`
2. ✅ **Probar endpoints**: http://localhost:8000/docs
3. ✅ **Crear tu primer perfil**: POST a `/api/v1/profiles`
4. ✅ **Ver en Supabase**: Revisa los datos en el Table Editor
5. ✅ **Configurar Storage**: Para subir imágenes de perfil y logos
6. ✅ **Configurar Authentication**: Para proteger endpoints

---

¿Preguntas? Abre un issue en GitHub o consulta la [documentación principal](./API_SETUP.md).
