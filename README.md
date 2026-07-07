# Akitoi

Tu hub de contacto profesional en un solo lugar.

## Propósito

**Akitoi** es una plataforma web para crear un hub de BIO personalizado para personas y empresas, centralizando toda tu información de contacto en un único lugar accesible y profesional.

### Características principales

- **Hub de contacto completo**: Centraliza todos tus canales de comunicación
  - Enlaces directos a WhatsApp
  - Email de contacto
  - Perfiles de redes sociales (LinkedIn, Twitter, Instagram, etc.)
  - Sitio web corporativo o personal
  - Perfil de usuario LLM
  - AI Agent personalizado

- **Accesibilidad web**: Accede a tu hub desde cualquier dispositivo con navegador

- **QR personalizado**: Genera automáticamente un código QR con link corto para compartir fácilmente

- **Personalización completa**:
  - Logo de empresa personalizable
  - Imagen de perfil de la persona de contacto
  - Paleta de colores de fondo personalizada
  - Diseño responsive y moderno

- **Dashboard de analíticas**: Registra y visualiza estadísticas de acceso a tu hub BIO
  - Número de visitas
  - Fuentes de tráfico
  - Clics en enlaces
  - Métricas de engagement

- **Capa móvil (MVP)**: El hub se guarda en la agenda del teléfono
  - vCard (.vcf) con solo datos básicos y públicos → agenda nativa iOS/Android
  - QR real (URL del hub o vCard completa offline) + PNG para fondo de pantalla
  - Payload NFC/NDEF para compartir con un tap (tags NTAG / HCE)
  - Asistente de contacto intermediario (el visitante nunca ve tus canales privados)
  - Ver [docs/MVP_MOVIL.md](docs/MVP_MOVIL.md)

### Stack técnico

El proyecto está construido con las mejores prácticas de la industria:

**Backend:**
- **API**: FastAPI + Python 3.9+
- **Base de datos**: Supabase (PostgreSQL)
- **ORM**: SQLAlchemy + Alembic migrations
- **Gestión de dependencias**: `pyproject.toml`
- **Calidad de código**: Ruff, Black, MyPy
- **Testing**: pytest

**Frontend:**
- **Framework**: Next.js 14 con App Router
- **UI**: React 18 + TypeScript 5.3
- **Estilos**: Tailwind CSS 3.4
- **Iconos**: Lucide React
- **Deploy**: Vercel

**Arquitectura:**
- **API REST**: FastAPI con documentación OpenAPI
- **SSR**: Server-Side Rendering con Next.js
- **Analytics**: Tracking automático de eventos
- **CORS**: Configurado para desarrollo y producción

## Requisitos

- Python 3.9 o superior
- pip (gestor de paquetes de Python)

## Instalación

### Instalación básica

```bash
# Clonar el repositorio
git clone https://github.com/oraculoweb/akitoi.git
cd akitoi

# Crear un entorno virtual
python -m venv venv

# Activar el entorno virtual
# En Linux/Mac:
source venv/bin/activate
# En Windows:
# venv\Scripts\activate

# Instalar el paquete
pip install -e .
```

### Instalación para desarrollo

```bash
# Instalar con dependencias de desarrollo
pip install -e ".[dev]"
```

## Uso básico

Una vez instalado el proyecto, podrás:

1. **Crear tu hub de BIO personalizado**
   - Configura tu perfil con información de contacto
   - Sube tu logo y foto de perfil
   - Personaliza colores y diseño

2. **Generar tu QR y link corto**
   - Obtén un código QR único para compartir
   - Link corto fácil de recordar y distribuir

3. **Gestionar tus enlaces**
   - Agrega enlaces a WhatsApp, email, redes sociales
   - Configura tu perfil LLM y AI Agent
   - Organiza tus canales de contacto

4. **Monitorear analíticas**
   - Accede al dashboard de estadísticas
   - Visualiza visitas y engagement
   - Analiza el rendimiento de tu hub

```python
# Ejemplo de uso de la API (en desarrollo)
import akitoi

# Crear un nuevo hub de BIO
hub = akitoi.create_hub(
    name="Mi Empresa",
    logo="path/to/logo.png",
    profile_image="path/to/photo.jpg",
    theme_colors={"primary": "#007bff", "background": "#ffffff"}
)

# Agregar enlaces de contacto
hub.add_contact("whatsapp", "+34123456789")
hub.add_contact("email", "contacto@miempresa.com")
hub.add_contact("linkedin", "https://linkedin.com/in/usuario")

# Generar QR y obtener link
qr_code = hub.generate_qr()
short_link = hub.get_short_link()
```

## Estructura del proyecto

```
akitoi/
├── src/
│   └── akitoi/          # Código fuente principal
│       └── __init__.py
├── tests/               # Tests unitarios y de integración
│   └── __init__.py
├── docs/                # Documentación adicional
├── .gitignore          # Archivos ignorados por git
├── pyproject.toml      # Configuración del proyecto y dependencias
└── README.md           # Este archivo
```

## Desarrollo

### Ejecutar tests

```bash
pytest
```

### Ejecutar linting

```bash
# Verificar código con Ruff
ruff check src/ tests/

# Formatear código con Black
black src/ tests/

# Verificar tipos con MyPy
mypy src/
```

### Formatear código automáticamente

```bash
black src/ tests/
ruff check --fix src/ tests/
```

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## Roadmap

### ✅ Fase 1: Profile Management MVP (Completado)
- [x] Sistema de creación de perfiles de usuario
- [x] API REST con FastAPI
- [x] Gestión de enlaces de contacto (WhatsApp, email, social media)
- [x] Editor de personalización (logo, imagen, colores)
- [x] Storage JSON para desarrollo rápido

### ✅ Fase 2: Modelo DB para Perfiles - Supabase (Completado)
- [x] Integración con Supabase PostgreSQL
- [x] Modelos SQLAlchemy optimizados
- [x] Migraciones con Alembic
- [x] Índices y constraints para rendimiento
- [x] Scripts de inicialización y verificación
- [x] Funciones de utilidad para queries comunes

### ✅ Fase 3: Frontend Next.js + Vercel (Completado)
- [x] Aplicación Next.js 14 con TypeScript y Tailwind CSS
- [x] Página de perfil dinámico [slug] con SSR
- [x] Cliente API para consumir FastAPI
- [x] Tracking automático de vistas y clicks
- [x] Componentes reutilizables (ProfileView, LinkButton)
- [x] Configuración de CORS en backend
- [x] Variables de entorno configuradas
- [x] Deploy automático en Vercel configurado
- [x] Documentación completa del frontend

### 📋 Fase 4: Features Avanzados
- [ ] Generador de QR codes
- [ ] Sistema de links cortos personalizados
- [ ] Integración con LLM user profiles
- [ ] Soporte para AI Agents personalizados
- [ ] Temas prediseñados y templates
- [ ] Supabase Storage para imágenes
- [ ] Supabase Auth para autenticación

### 📋 Fase 5: Infrastructure
- [ ] Configurar CI/CD
- [ ] Sistema de caché con Redis
- [ ] Rate limiting y seguridad
- [ ] CDN para assets estáticos
- [ ] Tests de integración completos
- [ ] Documentación completa de API

## Licencia

MIT License - ver archivo LICENSE para más detalles.

## Contacto

Akitoi Team - team@akitoi.dev

Project Link: [https://github.com/oraculoweb/akitoi](https://github.com/oraculoweb/akitoi)
