# ⚡ Quick Start - Akitoi Frontend

## 🎯 Lo que necesitas saber

Este es el frontend de Akitoi construido con **Next.js 14**, que consume la API de FastAPI para mostrar perfiles de contacto personalizados.

## 🚀 Inicio Rápido (3 pasos)

### 1. Instalar Node.js

**macOS/Linux:**
```bash
# Verificar si ya lo tienes
node --version

# Si no lo tienes, instalar con Homebrew (macOS)
brew install node

# O descargar desde: https://nodejs.org/
```

### 2. Instalar dependencias

```bash
cd frontend
npm install
```

### 3. Iniciar desarrollo

```bash
npm run dev
```

✅ **Listo!** Visita http://localhost:3000

## 📦 ¿Qué incluye?

- ✅ Next.js 14 con App Router
- ✅ TypeScript configurado
- ✅ Tailwind CSS para estilos
- ✅ Cliente API listo para usar
- ✅ Página de perfil dinámico `[slug]`
- ✅ Tracking automático de analytics
- ✅ Deploy-ready para Vercel

## 🎨 Rutas disponibles

```
http://localhost:3000/              → Página de inicio
http://localhost:3000/juan-tello    → Perfil de ejemplo
http://localhost:3000/[cualquier-slug] → Perfil dinámico
```

## ⚙️ Configuración

### Variables de entorno (ya configuradas)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Para cambiar, edita `.env.local`

### CORS en backend (ya configurado)

El backend ya permite requests desde `http://localhost:3000`

## 📱 Características

### Perfil de usuario muestra:
- ✅ Nombre y biografía
- ✅ Imagen de perfil
- ✅ Logo de empresa
- ✅ Enlaces con iconos automáticos
- ✅ Tema personalizado (colores)
- ✅ Contador de visitas

### Analytics automático:
- ✅ Tracking de vistas al cargar
- ✅ Tracking de clicks en enlaces
- ✅ Sin configuración necesaria

## 🧪 Probar

### Ver perfil de ejemplo:
```bash
# Backend debe estar corriendo en :8000
npm run dev

# Visita en navegador:
http://localhost:3000/juan-tello
```

### Verificar tracking:
```bash
# En DevTools del navegador (F12)
# → Network → Buscar POST a /analytics/*/track
```

## 🚀 Deploy a Vercel

### Opción 1: GitHub (recomendado)
1. Push a GitHub
2. Importa en vercel.com
3. Configura `NEXT_PUBLIC_API_URL`
4. Deploy automático ✅

### Opción 2: CLI
```bash
npm i -g vercel
vercel --prod
```

## 📚 Documentación completa

- [README.md](README.md) - Documentación completa
- [START_HERE.md](START_HERE.md) - Guía detallada de inicio
- [../FASE_3_FRONTEND_COMPLETADA.md](../FASE_3_FRONTEND_COMPLETADA.md) - Detalles de implementación
- [../TEST_FASE_3.md](../TEST_FASE_3.md) - Guía de pruebas

## 🆘 Problemas comunes

### "Cannot connect to backend"
```bash
# Iniciar backend
cd ..
./scripts/run_dev.sh
```

### "Port 3000 in use"
```bash
# Usar otro puerto
PORT=3001 npm run dev
```

### "Module not found"
```bash
# Reinstalar
rm -rf node_modules
npm install
```

## 🎓 Stack

- Next.js 14.1
- React 18.2
- TypeScript 5.3
- Tailwind CSS 3.4
- Lucide React (iconos)

## ✨ Próximos pasos

1. ✅ Probar en local → http://localhost:3000
2. ✅ Personalizar estilos en `app/globals.css`
3. ✅ Crear más perfiles con la API
4. ✅ Deploy a Vercel
5. ✅ Configurar dominio personalizado

---

**¿Preguntas?** Lee [START_HERE.md](START_HERE.md) para guía paso a paso.

**¿Listo?** Ejecuta `npm run dev` y visita http://localhost:3000 🚀
