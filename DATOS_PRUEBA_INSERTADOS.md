# ✅ Datos de Prueba Insertados en Supabase

## 🎉 Resumen

Se ha creado exitosamente el perfil de **Juan Tello** con todos sus enlaces en la base de datos de Supabase.

---

## 👤 Perfil Creado

**ID:** `1608ecc2-d51a-42d0-964d-fcf325c10763`

| Campo | Valor |
|-------|-------|
| **Nombre** | Juan Tello |
| **Slug** | juan-tello |
| **Bio** | AI Educador \| Emprendedor \| Creador de Contenidos |
| **Publicado** | ✅ Sí |
| **Vistas** | 0 |
| **Imagen de perfil** | https://avatars.githubusercontent.com/u/1234567 |

### 🎨 Tema Personalizado

```json
{
  "primary_color": "#10b981",       // Verde
  "background_color": "#ffffff",     // Blanco
  "text_color": "#111827",          // Texto oscuro
  "font_family": "Inter, sans-serif"
}
```

---

## 🔗 Enlaces (8 totales)

| # | Tipo | Label | URL |
|---|------|-------|-----|
| 1 | whatsapp | Contáctame por WhatsApp | https://wa.me/51996780986 |
| 2 | email | Envíame un email | mailto:juan@lafabricaw.com |
| 3 | linkedin | LinkedIn | https://www.linkedin.com/in/jftello |
| 4 | website | AI Fácil Academy | https://aprendeaifacil.com |
| 5 | youtube | YouTube AI Fácil | https://www.youtube.com/@aifacil |
| 6 | whatsapp | Canal WhatsApp AI Fácil | https://whatsapp.com/channel/0029Va1SG9Y5kg7BvYQcGA3g |
| 7 | tiktok | TikTok | https://www.tiktok.com/@oraculowebtok |
| 8 | twitter | X (Twitter) | https://x.com/oraculoweb |

---

## 🔍 Verificar en Supabase Dashboard

1. Ve a https://app.supabase.com
2. Abre tu proyecto **"akitoi"**
3. Click en **"Table Editor"** en el menú lateral
4. Selecciona la tabla **"profiles"**
5. Deberías ver el perfil de Juan Tello
6. Selecciona la tabla **"links"**
7. Deberías ver los 8 enlaces ordenados

---

## 🚀 Consultar los Datos

### Usando Python

```python
from src.akitoi.database import SessionLocal, ProfileDB, LinkDB
from src.akitoi.database.utils import get_profile_by_slug

db = SessionLocal()

# Obtener perfil
profile = get_profile_by_slug(db, "juan-tello")
print(f"Perfil: {profile.name}")
print(f"Bio: {profile.bio}")

# Obtener enlaces
links = db.query(LinkDB).filter(LinkDB.profile_id == profile.id).order_by(LinkDB.order).all()
for link in links:
    print(f"{link.order}. {link.label}: {link.url}")

db.close()
```

### Usando SQL Directo

```sql
-- Ver el perfil
SELECT * FROM profiles WHERE slug = 'juan-tello';

-- Ver los enlaces
SELECT l.* FROM links l
JOIN profiles p ON l.profile_id = p.id
WHERE p.slug = 'juan-tello'
ORDER BY l."order";

-- Contar enlaces por tipo
SELECT type, COUNT(*) as count
FROM links l
JOIN profiles p ON l.profile_id = p.id
WHERE p.slug = 'juan-tello'
GROUP BY type;
```

---

## 📊 Estadísticas

- **1 perfil** creado
- **8 enlaces** insertados
- **3 tipos** de redes sociales: whatsapp (2), email (1), linkedin (1), website (1), youtube (1), tiktok (1), twitter (1)
- **0 eventos** de analytics (aún no hay vistas)

---

## 🔄 Volver a Ejecutar el Script

Si necesitas resetear los datos de prueba:

```bash
python3 scripts/seed_supabase.py
```

El script:
- ✅ Verifica la conexión a Supabase
- ✅ Elimina el perfil existente si ya existe
- ✅ Crea un nuevo perfil con todos los datos
- ✅ Inserta los 8 enlaces en orden
- ✅ Muestra un resumen completo

---

## 🎯 Próximos Pasos

### 1. Ver en Supabase Dashboard

Ve al Table Editor y explora las tablas `profiles` y `links` para ver los datos insertados.

### 2. Crear Más Perfiles de Prueba

Puedes modificar `scripts/seed_supabase.py` para crear más perfiles:

```python
# Crear perfil adicional
profile2 = ProfileDB(
    id=str(uuid.uuid4()),
    name="Otro Usuario",
    slug="otro-usuario",
    bio="Descripción del usuario",
    # ... etc
)
```

### 3. Insertar Eventos de Analytics

```python
from src.akitoi.database import SessionLocal, AnalyticsEventDB
from datetime import datetime

db = SessionLocal()

# Crear evento de vista
event = AnalyticsEventDB(
    profile_id="1608ecc2-d51a-42d0-964d-fcf325c10763",
    event_type="view",
    event_metadata={"referrer": "google.com", "user_agent": "Chrome"}
)
db.add(event)
db.commit()
```

### 4. Probar las Funciones de Utilidad

```python
from src.akitoi.database.utils import (
    get_profile_analytics,
    increment_profile_view_count,
    increment_link_click_count
)

# Incrementar vistas
increment_profile_view_count(db, "1608ecc2-d51a-42d0-964d-fcf325c10763")

# Ver analytics
analytics = get_profile_analytics(db, "1608ecc2-d51a-42d0-964d-fcf325c10763")
print(analytics)
```

---

## 📁 Archivos Relacionados

- **Script de seed**: `scripts/seed_supabase.py`
- **Datos de referencia**: `examples/Juan-Tello.py`
- **Modelos de BD**: `src/akitoi/database/models.py`
- **Utilidades**: `src/akitoi/database/utils.py`

---

✅ **Datos insertados exitosamente en Supabase PostgreSQL**
