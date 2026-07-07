# Akitoi Móvil — Plan, Revisión y MVP

## 1. Revisión del proyecto (estado actual)

| Capa | Estado | Observaciones |
|------|--------|---------------|
| Modelos y core Python | ✅ Sólido | Profile/Link/Theme con tests |
| API FastAPI | ✅ Funcional | CRUD de perfiles + analytics sobre Supabase |
| Base de datos | ✅ Supabase | SQLAlchemy + Alembic |
| Frontend Next.js | ✅ Básico | Página de perfil en Vercel |
| **Capa móvil** | ✅ **Nueva (este MVP)** | vCard, QR real, NFC, asistente |

Correcciones aplicadas durante la revisión:
- `node_modules/` (8.218 archivos) estaba versionado → eliminado del repo y agregado a `.gitignore`.
- Bug en `POST /api/v1/profiles/{id}/links`: se construía `Link(type=..., label=...)` con argumentos que el modelo no acepta (`title`, `link_type`) → corregido.

## 2. Concepto: la BIO que vive en la agenda del teléfono

La innovación central del MVP: **el hub no se queda en la web — se
instala en la agenda de contactos del visitante**, revelando solo
datos básicos y públicos:

- Nombre, foto de persona o logo de empresa
- Resumen de 160 caracteres (privacidad: nunca la bio completa ni analytics)
- Teléfono, email, sitio web y perfiles sociales públicos
- El link al hub Akitoi queda embebido en el contacto (campo URL),
  así el contacto guardado "se actualiza" visitando el hub

## 3. Canales de transmisión del contacto

| Canal | Tecnología | Estado |
|-------|-----------|--------|
| Descarga directa | vCard 3.0 (`.vcf`) → agenda nativa iOS/Android | ✅ MVP |
| Escaneo visual | QR con URL del hub **o vCard completa offline** | ✅ MVP |
| Fondo de pantalla | PNG de alta resolución del QR para lock screen | ✅ MVP |
| **Tap inalámbrico (moderno)** | **NFC/NDEF**: payload listo para grabar en tags NTAG o emular con el teléfono | ✅ MVP |
| Compartir nativo | Web Share API (hoja de compartir del SO) | ✅ MVP |
| Proximidad avanzada | BLE advertising / Wi-Fi Aware / UWB (AirDrop-like) | 🔭 Futuro |

### ¿Por qué NFC como "lo más moderno que el QR"?
- Un tag NTAG213 cuesta centavos; se pega en una tarjeta, credencial o
  carcasa del teléfono.
- El visitante solo **acerca su teléfono**: sin cámara, sin app, sin luz.
- El payload NDEF generado por Akitoi lleva la URL del hub **y** la
  vCard completa: funciona incluso sin conexión.
- El mismo payload sirve para HCE (el teléfono emula el tag).

### Futuro (Fase siguiente)
- **BLE advertising**: difundir el slug del hub a teléfonos cercanos
  (estilo Nearby Share) desde una PWA/app nativa.
- **UWB**: apuntar el teléfono a otra persona para intercambiar hubs
  (requiere app nativa, hardware U1/UWB).
- **Live Contact Sync**: el contacto guardado se refresca contra el hub
  (CardDAV / suscripción).

## 4. Asistente intermediario

El visitante nunca ve los canales privados del dueño. Deja un mensaje
con el **asistente de contacto**:

1. `POST /m/{slug}/contact` valida y guarda la solicitud
   (honeypot anti-bots incluido).
2. El asistente genera un *handoff*: links de respuesta prellenados
   (WhatsApp `wa.me` / `mailto:`) para que el dueño responda desde su
   propio dispositivo.
3. Punto de enchufe natural para un **agente IA** (siguiente fase):
   filtrado, respuestas automáticas, agendamiento.

## 5. Endpoints del MVP móvil

```
GET  /m/{slug}                  Página móvil minimalista (HTML server-rendered)
GET  /m/{slug}/card             Tarjeta pública JSON (solo datos básicos)
GET  /m/{slug}/vcard            .vcf → guardar en la agenda del teléfono
GET  /m/{slug}/qr.svg           QR (content=url | content=vcard)
GET  /m/{slug}/wallpaper.png    QR alta resolución para fondo de pantalla
GET  /m/{slug}/nfc              Payload NDEF (hex/base64) para grabar tags NFC
POST /m/{slug}/contact          Mensaje al asistente intermediario
```

Reglas de privacidad aplicadas en todos los endpoints:
- Solo perfiles **publicados** (404 en caso contrario).
- Todo deriva de `ContactCard`: sin analytics, sin ids internos,
  sin links inactivos.

## 6. Probar en local

```bash
pip install -e ".[dev]"
uvicorn akitoi.api.main:app --reload
# abrir http://localhost:8000/m/<slug> desde el móvil (misma red)
```

## 7. Mejoras sugeridas (backlog priorizado)

1. **PWA instalable** del hub (manifest + service worker) → "app" sin stores.
2. **Agente IA en el asistente** (Claude API): triage, respuestas, agenda.
3. **Live Contact Sync** (CardDAV) para que el contacto guardado se actualice.
4. **BLE/Nearby share** desde PWA con Web Bluetooth donde esté disponible.
5. Editor visual de temas + previsualización del wallpaper QR.
6. Verificación de perfiles (badge) y dominios propios por empresa.
7. Rate limiting + captcha invisible en el asistente para producción.
