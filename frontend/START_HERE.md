# 🚀 Guía de Inicio Rápido - Akitoi Frontend

## Prerrequisitos

Antes de comenzar, asegúrate de tener instalado:

1. **Node.js 18+** - [Descargar aquí](https://nodejs.org/)
2. **Backend de Akitoi** corriendo en `http://localhost:8000`

## Pasos para iniciar

### 1. Instalar Node.js (si no lo tienes)

**macOS:**
```bash
# Opción 1: Usar Homebrew (recomendado)
brew install node

# Opción 2: Descargar desde https://nodejs.org/
```

**Verificar instalación:**
```bash
node --version  # Debería mostrar v18.x.x o superior
npm --version   # Debería mostrar 9.x.x o superior
```

### 2. Instalar dependencias

```bash
cd frontend
npm install
```

Este comando instalará todas las dependencias necesarias:
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Lucide React (iconos)

### 3. Configurar variables de entorno

```bash
# Ya existe el archivo .env.local con:
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Si necesitas cambiar la URL del backend, edita `.env.local`

### 4. Iniciar el servidor de desarrollo

```bash
npm run dev
```

El frontend estará disponible en: **http://localhost:3000**

## ✅ Pruebas básicas

### 1. Verificar página de inicio

Abre en tu navegador:
```
http://localhost:3000
```

Deberías ver la página de bienvenida de Akitoi.

### 2. Ver perfil de ejemplo

```
http://localhost:3000/juan-tello
```

Esto cargará el perfil de Juan Tello desde el backend.

### 3. Verificar tracking de analytics

Cada vez que visites un perfil o hagas click en un enlace, se registrará en analytics automáticamente.

## 📊 Estructura de URLs

- `/` - Página de inicio
- `/[slug]` - Perfil dinámico (ej: `/juan-tello`, `/mi-empresa`)

## 🔧 Comandos útiles

```bash
# Desarrollo
npm run dev          # Inicia servidor de desarrollo

# Producción
npm run build        # Construye para producción
npm start            # Inicia en modo producción

# Calidad de código
npm run lint         # Ejecuta ESLint
```

## 🐛 Troubleshooting

### Error: "Cannot connect to backend"

**Solución:** Asegúrate de que el backend está corriendo:

```bash
# En otra terminal, desde la raíz del proyecto
cd /Users/juantello/akitoi
./scripts/run_dev.sh
```

### Error: "Profile not found"

**Solución:** Verifica que el perfil existe en la base de datos:

```bash
curl http://localhost:8000/api/v1/profiles/juan-tello
```

### Error: "CORS policy"

**Solución:** Ya está configurado. Si persiste, verifica que el backend tenga `http://localhost:3000` en los orígenes permitidos.

## 📦 Deploy a Vercel

### Opción 1: GitHub (recomendado)

1. Sube tu código a GitHub
2. Ve a [vercel.com](https://vercel.com)
3. Importa el repositorio
4. Vercel detectará Next.js automáticamente
5. Configura la variable de entorno:
   - `NEXT_PUBLIC_API_URL` = URL de tu backend en producción

### Opción 2: CLI

```bash
# Instalar Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel

# Deploy a producción
vercel --prod
```

## 🎨 Personalización

### Cambiar colores por defecto

Edita `components/ProfileView.tsx`:

```typescript
const primaryColor = profile.theme?.primary_color || '#3b82f6'  // Azul
const backgroundColor = profile.theme?.background_color || '#ffffff'  // Blanco
const textColor = profile.theme?.text_color || '#1f2937'  // Gris oscuro
```

### Agregar más tipos de enlaces

Edita `components/LinkButton.tsx` y agrega más casos al switch:

```typescript
case 'tiktok':
  return <TikTok {...iconProps} />
```

## 📚 Documentación adicional

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Lucide Icons](https://lucide.dev/)

## ✨ Próximos pasos

1. Personaliza el diseño en `app/globals.css`
2. Agrega más componentes en `components/`
3. Implementa dashboard de analytics
4. Agrega autenticación de usuarios
5. Deploy a producción en Vercel

---

**¿Listo para empezar?** 🎉

```bash
cd frontend
npm install
npm run dev
```

Visita: http://localhost:3000
