# 🧪 Guía de Pruebas - Fase 3 Frontend

Esta guía te ayudará a verificar que todo funciona correctamente.

## Pre-requisitos

1. **Node.js instalado** (v18+)
2. **Backend corriendo** en http://localhost:8000
3. **Base de datos Supabase** con datos de prueba

## 📋 Checklist de Pruebas

### ✅ Parte 1: Verificar Instalación

```bash
# 1. Verificar Node.js
node --version
# Esperado: v18.x.x o superior

# 2. Ir al directorio frontend
cd frontend

# 3. Instalar dependencias
npm install
# Esperado: Sin errores, node_modules creado

# 4. Verificar archivos de configuración
ls -la | grep -E "(package.json|tsconfig.json|tailwind.config.ts)"
# Esperado: Ver los 3 archivos listados
```

### ✅ Parte 2: Verificar Backend

```bash
# 5. Verificar backend corriendo
curl http://localhost:8000/health
# Esperado: {"status": "healthy"}

# 6. Verificar CORS configurado
curl -I http://localhost:8000/api/v1/profiles/juan-tello
# Esperado: Ver headers Access-Control-Allow-Origin

# 7. Verificar perfil de prueba existe
curl http://localhost:8000/api/v1/profiles/juan-tello
# Esperado: JSON con datos del perfil
```

### ✅ Parte 3: Iniciar Frontend

```bash
# 8. Iniciar servidor de desarrollo
npm run dev
# Esperado:
# ✓ Ready in X ms
# ○ Local: http://localhost:3000

# 9. En otra terminal, verificar que responde
curl http://localhost:3000
# Esperado: HTML de la página de inicio
```

### ✅ Parte 4: Pruebas en Navegador

Abre tu navegador y visita:

#### Test 1: Página de Inicio
```
URL: http://localhost:3000
```

**Verificar:**
- [ ] Se carga correctamente
- [ ] Muestra "Bienvenido a Akitoi"
- [ ] Hay un botón "Ver perfil de ejemplo"
- [ ] Los estilos de Tailwind se aplican

#### Test 2: Perfil Dinámico
```
URL: http://localhost:3000/juan-tello
```

**Verificar:**
- [ ] Se carga el perfil desde el backend
- [ ] Se muestra el nombre "Juan Tello"
- [ ] Se muestra la biografía
- [ ] Se muestran los enlaces con iconos
- [ ] Los botones tienen el color correcto (#10b981)
- [ ] Contador de visitas aparece
- [ ] Footer "Powered by Akitoi" presente

#### Test 3: Tracking de Vistas
```
URL: http://localhost:3000/juan-tello
```

**Verificar en consola del navegador:**
1. Abre DevTools (F12)
2. Ve a Network
3. Recarga la página
4. Busca request a `/api/v1/analytics/juan-tello/track`
5. Debe haber un POST con `event_type: "view"`

**Verificar en backend:**
```bash
curl http://localhost:8000/api/v1/analytics/juan-tello/analytics
```
- [ ] `total_views` debe incrementar

#### Test 4: Tracking de Clicks
```
URL: http://localhost:3000/juan-tello
```

**Verificar:**
1. Click en cualquier botón de enlace
2. En DevTools → Network
3. Debe haber POST a `/api/v1/analytics/juan-tello/track`
4. Con `event_type: "click"`
5. El enlace debe abrirse en nueva pestaña

**Verificar en backend:**
```bash
curl http://localhost:8000/api/v1/analytics/juan-tello/analytics
```
- [ ] `total_clicks` debe incrementar
- [ ] `clicks_by_link` debe mostrar el enlace clickeado

#### Test 5: Perfil No Encontrado
```
URL: http://localhost:3000/perfil-que-no-existe
```

**Verificar:**
- [ ] Muestra página 404 personalizada
- [ ] Título "Perfil no encontrado"
- [ ] Botón "Volver al inicio" funciona

#### Test 6: Responsive Design
```
URL: http://localhost:3000/juan-tello
```

**Verificar:**
1. Abre DevTools (F12)
2. Activa modo responsive (Ctrl+Shift+M)
3. Prueba diferentes resoluciones:
   - [ ] Mobile (375px)
   - [ ] Tablet (768px)
   - [ ] Desktop (1024px)
4. Todo debe verse bien en todas las resoluciones

### ✅ Parte 5: Verificar Personalización de Temas

```bash
# Crear un perfil con tema personalizado
curl -X POST http://localhost:8000/api/v1/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "slug": "test-theme",
    "bio": "Testing custom theme",
    "theme": {
      "primary_color": "#ef4444",
      "background_color": "#f3f4f6",
      "text_color": "#1f2937"
    },
    "links": [
      {
        "title": "Test Link",
        "url": "https://example.com",
        "link_type": "custom"
      }
    ],
    "is_published": true
  }'
```

Visita: http://localhost:3000/test-theme

**Verificar:**
- [ ] Botones son rojos (#ef4444)
- [ ] Fondo es gris claro (#f3f4f6)
- [ ] Texto es gris oscuro (#1f2937)

### ✅ Parte 6: Verificar Tipos de Enlaces

Visita: http://localhost:3000/juan-tello

**Verificar iconos correctos:**
- [ ] WhatsApp → Icono de mensaje
- [ ] Email → Icono de correo
- [ ] LinkedIn → Icono de LinkedIn
- [ ] Twitter → Icono de Twitter
- [ ] GitHub → Icono de GitHub
- [ ] Website → Icono de globo

### ✅ Parte 7: SEO y Metadata

```bash
# Ver metadata de la página
curl http://localhost:3000/juan-tello | grep -E "(title|description|meta)"
```

**Verificar en navegador:**
1. View Page Source (Ctrl+U)
2. Buscar en head:
   - [ ] `<title>Juan Tello | Akitoi</title>`
   - [ ] `<meta name="description" content="...">`

---

## 🚨 Troubleshooting

### Error: "Cannot connect to backend"

```bash
# Verificar backend está corriendo
curl http://localhost:8000/health

# Si no responde, iniciar backend
cd /Users/juantello/akitoi
./scripts/run_dev.sh
```

### Error: "Module not found"

```bash
# Reinstalar dependencias
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Error: "Port 3000 already in use"

```bash
# Matar proceso en puerto 3000
lsof -ti:3000 | xargs kill -9

# O usar otro puerto
PORT=3001 npm run dev
```

### Error: "CORS policy"

Verificar en `src/akitoi/api/main.py`:
```python
origins = [
    "http://localhost:3000",  # Debe estar presente
    ...
]
```

Reiniciar backend después de cambios.

---

## ✅ Checklist Final

- [ ] Frontend inicia sin errores
- [ ] Página de inicio se carga
- [ ] Perfil dinámico se carga desde backend
- [ ] Tracking de vistas funciona
- [ ] Tracking de clicks funciona
- [ ] Página 404 funciona
- [ ] Responsive design funciona
- [ ] Temas personalizados funcionan
- [ ] Todos los iconos se muestran
- [ ] SEO metadata presente
- [ ] No hay errores en consola
- [ ] No hay warnings de CORS

---

## 📊 Resultado Esperado

Si todas las pruebas pasan:

```
✅ Fase 3 Frontend - 100% Funcional

- Next.js 14 configurado correctamente
- Integración con FastAPI funcionando
- Tracking de analytics operativo
- Temas personalizados aplicándose
- SEO optimizado
- Deploy-ready para Vercel
```

---

## 🎯 Próximos Pasos Después de Probar

1. **Deploy a Vercel**
   ```bash
   npm i -g vercel
   cd frontend
   vercel
   ```

2. **Configurar dominio personalizado**
   - En Vercel Dashboard
   - Settings → Domains

3. **Agregar más perfiles**
   - Usar POST /api/v1/profiles
   - Personalizar temas
   - Agregar enlaces

4. **Monitorear analytics**
   - Ver /api/v1/analytics/trending
   - Analizar datos de visitas

---

**¡Listo para producción!** 🚀

Si todas las pruebas pasan, tu frontend está completamente funcional y listo para desplegarse en Vercel.
