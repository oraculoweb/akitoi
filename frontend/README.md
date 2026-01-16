# Akitoi Frontend

Frontend de la plataforma Akitoi construido con Next.js 14, TypeScript y Tailwind CSS.

## Características

- **Next.js 14** con App Router
- **TypeScript** para type safety
- **Tailwind CSS** para estilos
- **Server-Side Rendering (SSR)** para perfiles dinámicos
- **Analytics tracking** automático de vistas y clicks
- **Responsive design** para todos los dispositivos

## Requisitos previos

- Node.js 18+
- npm o yarn
- Backend de Akitoi corriendo en `http://localhost:8000`

## Instalación

```bash
# Instalar dependencias
npm install

# o con yarn
yarn install
```

## Configuración

1. Copia el archivo de variables de entorno:

```bash
cp .env.example .env.local
```

2. Configura la URL del backend en `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Desarrollo

```bash
# Iniciar servidor de desarrollo
npm run dev

# El frontend estará disponible en http://localhost:3000
```

## Construcción

```bash
# Construir para producción
npm run build

# Iniciar en modo producción
npm start
```

## Estructura del proyecto

```
frontend/
├── app/
│   ├── [slug]/           # Páginas dinámicas de perfiles
│   │   ├── page.tsx      # Página principal del perfil
│   │   └── not-found.tsx # Página 404
│   ├── layout.tsx        # Layout principal
│   ├── page.tsx          # Página de inicio
│   └── globals.css       # Estilos globales
├── components/
│   ├── ProfileView.tsx   # Componente de vista de perfil
│   └── LinkButton.tsx    # Botón de enlace con iconos
├── lib/
│   └── api.ts           # Cliente de API
├── public/              # Assets estáticos
├── .env.local          # Variables de entorno (no commitear)
├── .env.example        # Ejemplo de variables de entorno
└── package.json        # Dependencias
```

## Deploy en Vercel

### Opción 1: Deploy automático desde GitHub

1. Conecta tu repositorio a Vercel
2. Vercel detectará automáticamente Next.js
3. Configura las variables de entorno:
   - `NEXT_PUBLIC_API_URL`: URL de tu backend en producción

### Opción 2: Deploy manual

```bash
# Instalar Vercel CLI
npm i -g vercel

# Deploy
vercel

# Deploy a producción
vercel --prod
```

### Variables de entorno en Vercel

En el dashboard de Vercel, configura:

- **NEXT_PUBLIC_API_URL**: URL del backend (ej: `https://api.akitoi.com`)

## Rutas

- `/` - Página de inicio
- `/[slug]` - Perfil de usuario dinámico (ej: `/juan-tello`)

## Componentes principales

### ProfileView

Componente principal que renderiza un perfil de usuario con:
- Imagen de perfil
- Logo
- Bio
- Enlaces con tracking de clicks
- Contador de visitas

### LinkButton

Botón de enlace con:
- Iconos automáticos según el tipo
- Tracking de clicks
- Apertura en nueva pestaña
- Animaciones hover

## Cliente API

El cliente API (`lib/api.ts`) proporciona métodos para:

- `getProfile(slug)` - Obtener perfil por slug
- `listProfiles()` - Listar todos los perfiles
- `trackEvent(slug, eventType, linkId)` - Trackear eventos
- `getAnalytics(slug, days)` - Obtener analytics

## Tracking de Analytics

El tracking de analytics se realiza automáticamente:

- **View tracking**: Al cargar la página del perfil
- **Click tracking**: Al hacer click en cualquier enlace

## Personalización de temas

Cada perfil puede tener su propio tema con:

- `primary_color` - Color principal para botones
- `background_color` - Color de fondo
- `text_color` - Color de texto
- `logo_url` - URL del logo
- `profile_image_url` - URL de la imagen de perfil

## Tecnologías utilizadas

- **Next.js 14** - React framework con SSR
- **React 18** - Librería de UI
- **TypeScript** - Superset de JavaScript con tipos
- **Tailwind CSS** - Framework de CSS utility-first
- **Lucide React** - Iconos modernos
- **Vercel** - Platform de deployment

## Troubleshooting

### El frontend no puede conectar con el backend

Verifica que:
1. El backend está corriendo en `http://localhost:8000`
2. La variable `NEXT_PUBLIC_API_URL` está correctamente configurada
3. CORS está habilitado en el backend para `http://localhost:3000`

### Error 404 en perfiles

Verifica que:
1. El slug del perfil existe en la base de datos
2. El perfil está publicado (`is_published: true`)
3. El backend está respondiendo correctamente

## Licencia

MIT License - ver archivo LICENSE para más detalles.
