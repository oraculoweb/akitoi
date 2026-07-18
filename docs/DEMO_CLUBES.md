# Demo de punta a punta — Akitoi Clubes

## Preparación (una sola vez)

```bash
# Terminal 1 — backend
pip install -e ".[dev]"
uvicorn akitoi.api.main:app --reload --port 8000

# Terminal 2 — datos de demo (club ficticio + 5 socios + admin)
python scripts/seed_demo_club.py
# → imprime el TOKEN de login del panel y los links de carnet

# Terminal 3 — frontend
cd frontend && npm install && npm run dev   # http://localhost:3000
```

Sin proyecto Supabase configurado, el panel usa el **modo demo local**:
se pega el token que imprime el seed (firmado con el fallback de
desarrollo; inválido contra cualquier despliegue real). Con
`NEXT_PUBLIC_SUPABASE_URL` + `NEXT_PUBLIC_SUPABASE_ANON_KEY` el login
es Supabase Auth real (email+contraseña o magic link).

## Secuencia de demo (5 minutos)

1. **Entrar como admin** — abre `http://localhost:3000/admin`, pega el
   token del seed → aparece el panel de **Club Andino Demo** con los
   5 socios y sus estados a color (verde/rojo/ámbar/gris).

2. **Subir un padrón** — botón *Subir padrón*, elige un CSV (puedes
   descargar la *Plantilla CSV* desde el mismo panel). El panel
   muestra el resultado: `✔ creados · ↻ actualizados · − bajas · ⚠
   errores` con el detalle por fila de los errores, sin abortar la
   carga.

3. **Emitir el carnet de un socio vigente** — botón *Carnet* en la fila
   de Ana Pérez → se abre la VISTA 2: credencial con nombre, club y el
   **QR dinámico firmado**. Escanéalo con el teléfono → se abre la
   página de veredicto **VIGENTE en verde** (VISTA 3, servida por el
   backend a través del rewrite `/verify/...`).

4. **Suspender en vivo** — de vuelta en el panel, botón *Suspender* en
   la fila de Ana. Vuelve a escanear **el mismo QR** del paso 3 →
   ahora el veredicto es **SUSPENDIDO en rojo**. Nada se reemitió: la
   revocación es instantánea porque la vigencia se consulta en vivo.

5. **Cerrar el ciclo** — botón *Descargar reporte* → CSV con el estado
   efectivo de cada socio y su fecha de última actualización
   (incluye las bajas para auditoría).

## Qué sigue público (sin login)

- `/verify/{token}` — la puerta escanea sin autenticarse.
- `/card/{token}` — el carnet del socio.
- Todo el free tier (hub `/m/{slug}`, `.vcf`, QR estático).
