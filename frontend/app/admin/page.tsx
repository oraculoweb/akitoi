'use client'

/**
 * VISTA 1 — Panel del club (admin).
 *
 * Login con Supabase Auth (magic link o email+password; en demo local
 * se pega un token generado con scripts/make_demo_token.py). Todas
 * las llamadas de gestión viajan con Authorization: Bearer.
 */

import { useCallback, useEffect, useRef, useState } from 'react'
import {
  clubsApi,
  ClubMember,
  ImportResult,
  Organization,
} from '@/lib/api'
import {
  clearToken,
  sendMagicLink,
  signInWithPassword,
  storedToken,
  storeToken,
  supabaseConfigured,
  tokenFromUrlHash,
} from '@/lib/supabase'
import StatusBadge from '@/components/clubs/StatusBadge'

export default function AdminPage() {
  const [token, setToken] = useState<string | null>(null)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    const fromHash = tokenFromUrlHash()
    if (fromHash) {
      storeToken(fromHash)
      window.history.replaceState(null, '', window.location.pathname)
    }
    setToken(fromHash || storedToken())
    setReady(true)
  }, [])

  const handleLogout = () => {
    clearToken()
    setToken(null)
  }

  if (!ready) return null
  return (
    <main className="min-h-screen bg-gray-50 py-10 px-4">
      <div className="max-w-4xl mx-auto">
        <header className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold">
            Akitoi <span className="text-blue-600">Clubes</span>
          </h1>
          {token && (
            <button
              onClick={handleLogout}
              className="text-sm text-gray-500 hover:text-gray-800 underline"
            >
              Cerrar sesión
            </button>
          )}
        </header>
        {token ? (
          <Dashboard token={token} onAuthError={handleLogout} />
        ) : (
          <LoginPanel onToken={(t) => { storeToken(t); setToken(t) }} />
        )}
      </div>
    </main>
  )
}

// --- Login ---

function LoginPanel({ onToken }: { onToken: (token: string) => void }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [pasted, setPasted] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const run = async (action: () => Promise<void>) => {
    setBusy(true)
    setError('')
    setMessage('')
    try {
      await action()
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : 'Error inesperado')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-8 max-w-md mx-auto space-y-6">
      <h2 className="text-xl font-semibold text-center">
        Acceso de administrador
      </h2>

      {supabaseConfigured ? (
        <form
          className="space-y-3"
          onSubmit={(e) => {
            e.preventDefault()
            run(async () => onToken(await signInWithPassword(email, password)))
          }}
        >
          <input
            type="email"
            required
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full border rounded-lg px-4 py-3"
          />
          <input
            type="password"
            placeholder="Contraseña"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full border rounded-lg px-4 py-3"
          />
          <button
            type="submit"
            disabled={busy || !password}
            className="w-full py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {busy ? 'Entrando…' : 'Entrar'}
          </button>
          <button
            type="button"
            disabled={busy || !email}
            onClick={() =>
              run(async () => {
                await sendMagicLink(email)
                setMessage('Revisa tu correo: te enviamos un enlace mágico.')
              })
            }
            className="w-full py-3 border border-blue-600 text-blue-600 rounded-lg font-semibold hover:bg-blue-50 disabled:opacity-50 transition-colors"
          >
            Enviarme un enlace mágico
          </button>
        </form>
      ) : (
        <p className="text-sm text-gray-500 text-center">
          Supabase Auth no está configurado (define
          NEXT_PUBLIC_SUPABASE_URL y NEXT_PUBLIC_SUPABASE_ANON_KEY).
        </p>
      )}

      <details className="text-sm text-gray-600" open={!supabaseConfigured}>
        <summary className="cursor-pointer font-medium">
          Modo demo local (pegar token)
        </summary>
        <p className="mt-2 mb-2">
          Genera un token con{' '}
          <code className="bg-gray-100 px-1 rounded">
            python scripts/make_demo_token.py
          </code>{' '}
          y pégalo aquí:
        </p>
        <textarea
          rows={3}
          value={pasted}
          onChange={(e) => setPasted(e.target.value)}
          className="w-full border rounded-lg px-3 py-2 font-mono text-xs"
          placeholder="eyJhbGciOi..."
        />
        <button
          disabled={!pasted.trim()}
          onClick={() => onToken(pasted.trim())}
          className="mt-2 w-full py-2 bg-gray-800 text-white rounded-lg font-semibold disabled:opacity-50"
        >
          Usar token
        </button>
      </details>

      {message && <p className="text-green-700 text-sm">{message}</p>}
      {error && <p className="text-red-600 text-sm">✖ {error}</p>}
    </div>
  )
}

// --- Dashboard ---

function Dashboard({
  token,
  onAuthError,
}: {
  token: string
  onAuthError: () => void
}) {
  const [orgs, setOrgs] = useState<Organization[] | null>(null)
  const [org, setOrg] = useState<Organization | null>(null)
  const [members, setMembers] = useState<ClubMember[]>([])
  const [showBajas, setShowBajas] = useState(false)
  const [importResult, setImportResult] = useState<ImportResult | null>(null)
  const [busy, setBusy] = useState('')
  const [error, setError] = useState('')
  const [newClubName, setNewClubName] = useState('')
  const fileInput = useRef<HTMLInputElement>(null)

  const fail = useCallback(
    (exc: unknown) => {
      const message = exc instanceof Error ? exc.message : 'Error inesperado'
      if (message.includes('401') || message.toLowerCase().includes('token')) {
        onAuthError()
        return
      }
      setError(message)
    },
    [onAuthError]
  )

  const refreshMembers = useCallback(
    (orgId: string, includeBajas: boolean) => {
      clubsApi
        .listMembers(token, orgId, includeBajas)
        .then(setMembers)
        .catch(fail)
    },
    [token, fail]
  )

  useEffect(() => {
    clubsApi
      .listMyOrganizations(token)
      .then((list) => {
        setOrgs(list)
        if (list.length > 0) setOrg(list[0])
      })
      .catch(fail)
  }, [token, fail])

  useEffect(() => {
    if (org) refreshMembers(org.id, showBajas)
  }, [org, showBajas, refreshMembers])

  if (orgs === null) {
    return <p className="text-center text-gray-500">Cargando tus clubes…</p>
  }

  if (!org) {
    return (
      <div className="bg-white rounded-lg shadow p-8 max-w-md mx-auto space-y-4">
        <h2 className="text-xl font-semibold">Crea tu club</h2>
        <input
          value={newClubName}
          onChange={(e) => setNewClubName(e.target.value)}
          placeholder="Nombre del club"
          className="w-full border rounded-lg px-4 py-3"
        />
        <button
          disabled={!newClubName.trim() || busy === 'create'}
          onClick={async () => {
            setBusy('create')
            try {
              const created = await clubsApi.createOrganization(
                token,
                newClubName.trim()
              )
              setOrgs([created])
              setOrg(created)
            } catch (exc) {
              fail(exc)
            } finally {
              setBusy('')
            }
          }}
          className="w-full py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
        >
          {busy === 'create' ? 'Creando…' : 'Crear club'}
        </button>
        {error && <p className="text-red-600 text-sm">✖ {error}</p>}
      </div>
    )
  }

  const act = async (label: string, action: () => Promise<unknown>) => {
    setBusy(label)
    setError('')
    try {
      await action()
      refreshMembers(org.id, showBajas)
    } catch (exc) {
      fail(exc)
    } finally {
      setBusy('')
    }
  }

  const openCard = async (member: ClubMember) => {
    setBusy(`card-${member.id}`)
    try {
      const card = await clubsApi.issueCard(token, org.id, member.id)
      const cardToken = card.verify_url.split('/').pop() as string
      window.open(`/card/${cardToken}`, '_blank')
    } catch (exc) {
      fail(exc)
    } finally {
      setBusy('')
    }
  }

  return (
    <div className="space-y-6">
      {/* Club header */}
      <div className="bg-white rounded-lg shadow p-6 flex items-center gap-4">
        {org.logo_url && (
          <img src={org.logo_url} alt="Logo" className="h-12 object-contain" />
        )}
        <div className="flex-1">
          <h2 className="text-2xl font-bold">{org.name}</h2>
          <p className="text-sm text-gray-500">
            {members.length} socios {showBajas ? '(incluye bajas)' : 'activos'}
          </p>
        </div>
        {orgs.length > 1 && (
          <select
            value={org.id}
            onChange={(e) =>
              setOrg(orgs.find((o) => o.id === e.target.value) || org)
            }
            className="border rounded-lg px-3 py-2 text-sm"
          >
            {orgs.map((o) => (
              <option key={o.id} value={o.id}>
                {o.name}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Roster actions */}
      <div className="bg-white rounded-lg shadow p-6 flex flex-wrap gap-3 items-center">
        <input
          ref={fileInput}
          type="file"
          accept=".csv,.xlsx,.xls"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (!file) return
            act('import', async () =>
              setImportResult(await clubsApi.importRoster(token, org.id, file))
            )
            e.target.value = ''
          }}
        />
        <button
          onClick={() => fileInput.current?.click()}
          disabled={busy === 'import'}
          className="px-5 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {busy === 'import' ? 'Importando…' : '⬆ Subir padrón (CSV/XLSX)'}
        </button>
        <button
          onClick={() =>
            act('export', () => clubsApi.downloadExport(token, org.id, 'csv'))
          }
          disabled={busy === 'export'}
          className="px-5 py-3 border border-blue-600 text-blue-600 rounded-lg font-semibold hover:bg-blue-50 disabled:opacity-50 transition-colors"
        >
          ⬇ Descargar reporte
        </button>
        <a
          href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/orgs/roster-template`}
          className="px-5 py-3 text-sm text-gray-600 underline hover:text-gray-900"
        >
          Plantilla CSV
        </a>
        <label className="ml-auto flex items-center gap-2 text-sm text-gray-600">
          <input
            type="checkbox"
            checked={showBajas}
            onChange={(e) => setShowBajas(e.target.checked)}
          />
          Ver bajas (auditoría)
        </label>
      </div>

      {error && (
        <p className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm">
          ✖ {error}
        </p>
      )}

      {/* Import feedback */}
      {importResult && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold mb-3">Resultado de la importación</h3>
          <div className="flex gap-6 text-sm">
            <span className="text-green-700 font-semibold">
              ✔ {importResult.created} creados
            </span>
            <span className="text-blue-700 font-semibold">
              ↻ {importResult.updated} actualizados
            </span>
            <span className="text-gray-600 font-semibold">
              − {importResult.deactivated} bajas
            </span>
            <span
              className={
                importResult.error_count
                  ? 'text-red-600 font-semibold'
                  : 'text-gray-400'
              }
            >
              ⚠ {importResult.error_count} errores
            </span>
          </div>
          {importResult.errors.length > 0 && (
            <ul className="mt-3 text-sm text-red-700 space-y-1">
              {importResult.errors.map((e, i) => (
                <li key={i}>
                  Fila {e.row ?? '?'}: {e.error}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Members table */}
      <div className="bg-white rounded-lg shadow overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 border-b">
              <th className="px-6 py-3">Socio</th>
              <th className="px-6 py-3">Rol</th>
              <th className="px-6 py-3">Estado</th>
              <th className="px-6 py-3">Vence</th>
              <th className="px-6 py-3 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {members.length === 0 && (
              <tr>
                <td colSpan={5} className="px-6 py-10 text-center text-gray-400">
                  Sin socios aún — sube el padrón para empezar.
                </td>
              </tr>
            )}
            {members.map((member) => (
              <tr key={member.id} className="border-b last:border-0">
                <td className="px-6 py-3">
                  <div className="font-medium">{member.name}</div>
                  <div className="text-gray-400">{member.email}</div>
                </td>
                <td className="px-6 py-3">{member.role}</td>
                <td className="px-6 py-3">
                  <StatusBadge estado={member.estado} />
                </td>
                <td className="px-6 py-3">
                  {member.valid_until?.slice(0, 10) || '—'}
                </td>
                <td className="px-6 py-3">
                  <div className="flex gap-2 justify-end">
                    {member.estado === 'vigente' ? (
                      <ActionButton
                        label="Suspender"
                        color="red"
                        busy={busy === `suspend-${member.id}`}
                        onClick={() =>
                          act(`suspend-${member.id}`, () =>
                            clubsApi.memberAction(token, org.id, member.id, 'suspend')
                          )
                        }
                      />
                    ) : (
                      <ActionButton
                        label="Reactivar"
                        color="green"
                        busy={busy === `reactivate-${member.id}`}
                        onClick={() =>
                          act(`reactivate-${member.id}`, () =>
                            clubsApi.memberAction(token, org.id, member.id, 'reactivate')
                          )
                        }
                      />
                    )}
                    {member.is_active && (
                      <ActionButton
                        label="Baja"
                        color="gray"
                        busy={busy === `baja-${member.id}`}
                        onClick={() =>
                          act(`baja-${member.id}`, () =>
                            clubsApi.memberAction(token, org.id, member.id, 'baja')
                          )
                        }
                      />
                    )}
                    <ActionButton
                      label="Carnet"
                      color="blue"
                      busy={busy === `card-${member.id}`}
                      onClick={() => openCard(member)}
                    />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

const BUTTON_COLORS: Record<string, string> = {
  red: 'border-red-500 text-red-600 hover:bg-red-50',
  green: 'border-green-600 text-green-700 hover:bg-green-50',
  gray: 'border-gray-400 text-gray-600 hover:bg-gray-100',
  blue: 'border-blue-600 text-blue-600 hover:bg-blue-50',
}

function ActionButton({
  label,
  color,
  busy,
  onClick,
}: {
  label: string
  color: string
  busy: boolean
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      disabled={busy}
      className={`px-3 py-1.5 rounded-lg border text-xs font-semibold transition-colors disabled:opacity-50 ${BUTTON_COLORS[color]}`}
    >
      {busy ? '…' : label}
    </button>
  )
}
