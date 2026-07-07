# Gestión del padrón del club (carga masiva)

El admin gestiona su club como **un solo archivo**: sube el padrón
completo (CSV o XLSX), y lo vuelve a subir cada vez que cambia. Akitoi
hace *upsert* por email y aplica los estados al instante.

## Plantilla

Descárgala de `GET /api/v1/orgs/roster-template` o créala con estas
columnas (la fila de cabecera es obligatoria; el orden no importa):

```csv
nombre,email,telefono,rol,estado,valid_until
Ana Pérez,ana@example.com,+51911222333,socio,vigente,2027-12-31
Luis Gómez,luis@example.com,,directivo,suspendido,2027-12-31
Rosa Díaz,rosa@example.com,+51944555666,socio,baja,
```

| Columna | Regla |
|---------|-------|
| `nombre` | Obligatorio |
| `email` | Obligatorio — **clave única de upsert** dentro del club |
| `telefono` | Opcional |
| `rol` | Opcional (default `socio`) |
| `estado` | `vigente` \| `suspendido` \| `vencido` \| `baja` (default `vigente`) |
| `valid_until` | Opcional. `YYYY-MM-DD` o `DD/MM/YYYY`; vacío = sin vencimiento |

## Semántica de importación (upsert por email)

- **Email nuevo** → se crea el socio con su membresía y estado.
- **Email existente** → se actualizan nombre/teléfono/rol y el estado
  de la membresía. **Aquí ocurre la revocación masiva**: subir el
  archivo con un socio en `suspendido` invalida su carnet en el
  siguiente escaneo, sin tocar nada más.
- **`estado = baja`** → **soft delete**: el registro persiste para
  auditoría (Ley 29733) pero sale de las vistas activas y su carnet
  queda inválido. Nunca hay borrado físico. Una fila posterior en
  `vigente` lo re-alta.
- **Fila malformada** → se reporta en el log con su número de fila y
  el motivo; el resto del archivo se importa igual (carga parcial).

Cada importación queda registrada (fecha/hora, creados, actualizados,
bajas, errores) y es consultable en el historial.

## Endpoints

```
GET    /api/v1/orgs/roster-template                  Plantilla CSV
POST   /api/v1/orgs                                  Crear club
GET    /api/v1/orgs/{id}/members[?include_inactive]  Padrón activo / auditoría
POST   /api/v1/orgs/{id}/members                     Alta individual
POST   /api/v1/orgs/{id}/members/{mid}/suspend       Suspender carnet
POST   /api/v1/orgs/{id}/members/{mid}/reactivate    Reactivar carnet
DELETE /api/v1/orgs/{id}/members/{mid}               Baja lógica (soft delete)
GET    /api/v1/orgs/{id}/members/{mid}/card          Emitir carnet (token + QR)
POST   /api/v1/orgs/{id}/roster/import               Subir padrón (CSV/XLSX)
GET    /api/v1/orgs/{id}/roster/imports              Historial de importaciones
GET    /api/v1/orgs/{id}/roster/export?format=csv|xlsx  Reporte actualizado
```

## Flujo completo

```
1. GET  roster-template        → el admin llena la plantilla
2. POST roster/import          → padrón cargado; log: {created: N, ...}
3. GET  members/{id}/card      → carnets emitidos (QR firmado → /verify/{token})
   ... el club opera; la puerta escanea /verify ...
4. El tesorero marca morosos como "suspendido" en el archivo
5. POST roster/import          → revocación masiva instantánea
6. GET  roster/export          → reporte con estados vigentes y fecha
                                 de última actualización de cada socio
```

El export incluye a los socios en `baja` (con ese estado) para que el
archivo descargado sirva como fuente completa de la siguiente edición.
