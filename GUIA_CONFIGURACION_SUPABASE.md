# 🚀 Guía Paso a Paso: Configurar Supabase para Akitoi

Sigue estos pasos exactos para obtener las credenciales de Supabase y configurar tu proyecto.

---

## 📋 Checklist Rápido

- [ ] Paso 1: Obtener Project Reference ID
- [ ] Paso 2: Obtener Database Password
- [ ] Paso 3: Obtener API Keys (anon y service_role)
- [ ] Paso 4: Generar SECRET_KEY
- [ ] Paso 5: Completar archivo .env
- [ ] Paso 6: Verificar conexión
- [ ] Paso 7: Inicializar base de datos

---

## 📍 PASO 1: Obtener Project Reference ID

### Instrucciones:

1. **Abre tu navegador** y ve a: https://app.supabase.com

2. **Selecciona tu proyecto** de la lista

3. **Haz click en el ícono de configuración** (⚙️) en el menú lateral izquierdo
   - Esto te llevará a "Project Settings"

4. **En la sección "General"**, busca el campo **"Reference ID"**
   - Se ve algo así: `abcdefghijklmnop`
   - Es un string de ~16 caracteres

5. **Copia el Reference ID**

### ✏️ Anota aquí:

```
Project Reference ID: _________________
```

---

## 🔒 PASO 2: Obtener Database Password

### Instrucciones:

1. **En Project Settings**, haz click en **"Database"** en el menú lateral

2. **Scroll hacia abajo** hasta la sección **"Connection string"**

3. **Opciones:**

   **A) Si RECUERDAS tu contraseña:**
   - Úsala directamente
   - Salta al Paso 3

   **B) Si NO RECUERDAS tu contraseña:**
   - Haz click en **"Reset database password"**
   - Haz click en **"Generate a password"** para crear una segura
   - **⚠️ IMPORTANTE**: Copia y guarda esta contraseña INMEDIATAMENTE
   - No podrás verla de nuevo después de cerrar el modal

### ✏️ Anota aquí:

```
Database Password: _________________
```

---

## 🔑 PASO 3: Obtener API Keys

### Instrucciones:

1. **En Project Settings**, haz click en **"API"** en el menú lateral

2. **Busca la sección "Project API keys"**

3. **Verás dos keys:**

   **A) anon (public) key:**
   - Empieza con `eyJhbG...`
   - Es una key JWT larga (~300 caracteres)
   - Haz click en el ícono de "Copy" al lado derecho

   **B) service_role (secret) key:**
   - También empieza con `eyJhbG...`
   - Es una key diferente a la anon
   - ⚠️ Esta es SECRETA, nunca la compartas públicamente
   - Haz click en "Reveal" y luego copia

### ✏️ Anota aquí:

```
SUPABASE_ANON_KEY: eyJhbG...

SUPABASE_SERVICE_ROLE_KEY: eyJhbG...
```

---

## 🎲 PASO 4: Generar SECRET_KEY

### Instrucciones:

1. **Abre una terminal** en la carpeta del proyecto

2. **Ejecuta este comando:**

   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Copia el resultado** (será algo como: `Xt3k9mP2qL8vR5nW1zJ4hC7bN6yF0aS9dG2eK5tM8wQ`)

### ✏️ Anota aquí:

```
SECRET_KEY: _________________
```

---

## 📝 PASO 5: Completar archivo .env

### Instrucciones:

1. **Abre el archivo `.env`** en tu editor de código

2. **Reemplaza los placeholders** con los valores que anotaste:

   ```env
   # Reemplaza YOUR-PROJECT-ID con tu Reference ID del Paso 1
   SUPABASE_URL=https://YOUR-PROJECT-ID.supabase.co

   # Pega tu anon key del Paso 3A
   SUPABASE_ANON_KEY=YOUR-ANON-KEY-HERE

   # Pega tu service_role key del Paso 3B
   SUPABASE_SERVICE_ROLE_KEY=YOUR-SERVICE-ROLE-KEY-HERE

   # Reemplaza YOUR-PASSWORD y YOUR-PROJECT-ID
   DATABASE_URL=postgresql://postgres:YOUR-PASSWORD@db.YOUR-PROJECT-ID.supabase.co:5432/postgres

   # Pega tu SECRET_KEY del Paso 4
   SECRET_KEY=GENERATE-A-SECURE-KEY-HERE
   ```

3. **Ejemplo completo** (con valores ficticios):

   ```env
   SUPABASE_URL=https://xyzabcdef123.supabase.co
   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJz...
   SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3M...
   DATABASE_URL=postgresql://postgres:MiP@ssw0rd2024!@db.xyzabcdef123.supabase.co:5432/postgres
   SECRET_KEY=Xt3k9mP2qL8vR5nW1zJ4hC7bN6yF0aS9dG2eK5tM8wQ
   ```

4. **Guarda el archivo**

---

## ✅ PASO 6: Verificar Conexión

### Instrucciones:

1. **Abre una terminal** en la carpeta del proyecto

2. **Ejecuta el script de verificación:**

   ```bash
   python3 scripts/check_db.py
   ```

3. **Deberías ver:**

   ```
   ============================================================
   Akitoi - Supabase Database Status Check
   ============================================================

   🔗 Database URL: postgresql://postgres:****@db.xxx.supabase.co:5432/postgres

   🔌 Testing database connection...
   ✅ Connected to PostgreSQL
      Version: PostgreSQL 15.x
   ```

4. **Si ves errores:**
   - Verifica que el Project Reference ID sea correcto
   - Verifica que la contraseña no tenga caracteres especiales sin escapar
   - Verifica que copiaste las keys completas

---

## 🗄️ PASO 7: Inicializar Base de Datos

### Instrucciones:

1. **Ejecuta el script de inicialización:**

   ```bash
   ./scripts/init_db.sh
   ```

2. **El script hará:**
   - ✅ Verificar conexión a Supabase
   - ✅ Ejecutar migraciones de Alembic
   - ✅ Crear tablas: profiles, links, analytics_events
   - ✅ Crear índices y constraints
   - ✅ Configurar triggers automáticos

3. **Deberías ver:**

   ```
   🚀 Akitoi - Supabase Database Initialization
   ============================================

   📋 Loading environment variables...
   ✅ Environment variables loaded

   🔌 Testing database connection...
   ✅ Database connection successful
   📊 PostgreSQL version: PostgreSQL 15.x

   ⬆️  Running Alembic migrations...
   This will create all necessary tables and indexes in Supabase

   INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial Supabase schema

   ✅ Database initialized successfully!

   📊 Your Supabase database now has:
      - profiles table (with indexes)
      - links table (with indexes)
      - analytics_events table (with indexes)
      - Automatic timestamp triggers

   🎉 You're ready to start using Akitoi!
   ```

---

## 🎉 PASO 8: Verificar en Dashboard de Supabase

### Instrucciones:

1. **Vuelve al dashboard de Supabase** en tu navegador

2. **Haz click en "Table Editor"** en el menú lateral

3. **Deberías ver las tablas:**
   - ✅ `profiles`
   - ✅ `links`
   - ✅ `analytics_events`
   - ✅ `alembic_version`

4. **Haz click en "profiles"** para ver la estructura:
   - Columnas: id, name, slug, bio, profile_image_url, etc.
   - Indexes: varios índices configurados

---

## 🚀 Próximos Pasos

Ahora que Supabase está configurado:

### 1. Ejecutar la API

```bash
./scripts/run_dev.sh
```

### 2. Visitar la documentación interactiva

Abre en tu navegador:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Crear tu primer perfil

```bash
curl -X POST "http://localhost:8000/api/v1/profiles" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Juan Tello",
    "slug": "juan-tello",
    "bio": "Tech entrepreneur & developer",
    "theme": {
      "primary_color": "#007bff",
      "background_color": "#ffffff",
      "text_color": "#333333"
    }
  }'
```

### 4. Ver el perfil en Supabase

Ve al Table Editor y verás tu perfil creado en la tabla `profiles`.

---

## 🆘 Troubleshooting

### Error: "could not connect to server"

**Solución:**
- Verifica que el `DATABASE_URL` tenga el formato correcto
- Verifica que el Project Reference ID sea correcto
- Verifica que tu IP no esté bloqueada en Supabase

### Error: "password authentication failed"

**Solución:**
- La contraseña es incorrecta
- Ve a Project Settings > Database > Reset database password
- Actualiza el `.env` con la nueva contraseña

### Error: "No module named 'sqlalchemy'"

**Solución:**
```bash
pip install -e .
```

---

## 📚 Recursos Adicionales

- [Documentación completa de Supabase](./SUPABASE_SETUP.md)
- [Guía de API](./API_SETUP.md)
- [README del proyecto](./README.md)

---

¿Preguntas? Revisa `SUPABASE_SETUP.md` para información más detallada.
