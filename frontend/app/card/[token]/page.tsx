'use client'

/**
 * VISTA 2 — Carnet digital del socio (público, sin login).
 *
 * Muestra la credencial con el QR DINÁMICO de verificación (token
 * firmado — no el .vcf del free tier). Los datos vienen del endpoint
 * público /verify/{token}?format=json; el QR de /verify/{token}/qr.svg.
 * Pensado para guardarse en el teléfono del socio.
 */

import { useEffect, useState } from 'react'
import { clubsApi, VerifyResult } from '@/lib/api'
import StatusBadge from '@/components/clubs/StatusBadge'

export default function CardPage({ params }: { params: { token: string } }) {
  const [result, setResult] = useState<VerifyResult | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    clubsApi
      .verify(params.token)
      .then(setResult)
      .catch((exc) =>
        setError(exc instanceof Error ? exc.message : 'Carnet inválido')
      )
  }, [params.token])

  if (error) {
    return (
      <Shell>
        <div className="bg-white rounded-2xl shadow-xl p-10 text-center">
          <p className="text-5xl mb-4">🚫</p>
          <h1 className="text-xl font-bold mb-2">Carnet no válido</h1>
          <p className="text-gray-500 text-sm">{error}</p>
        </div>
      </Shell>
    )
  }

  if (!result) {
    return (
      <Shell>
        <p className="text-gray-400">Cargando carnet…</p>
      </Shell>
    )
  }

  return (
    <Shell>
      <div className="w-full max-w-sm bg-white rounded-2xl shadow-xl overflow-hidden">
        {/* Club band */}
        <div className="bg-blue-600 text-white px-6 py-5 flex items-center gap-3">
          {result.organization.logo_url ? (
            <img
              src={result.organization.logo_url}
              alt="Logo"
              className="h-10 w-10 object-contain bg-white rounded-full p-1"
            />
          ) : (
            <span className="h-10 w-10 rounded-full bg-white/20 flex items-center justify-center text-lg font-bold">
              {result.organization.name.charAt(0)}
            </span>
          )}
          <div>
            <p className="text-xs uppercase tracking-widest opacity-80">
              Carnet de socio
            </p>
            <p className="font-bold leading-tight">
              {result.organization.name}
            </p>
          </div>
        </div>

        {/* Member */}
        <div className="px-6 pt-6 text-center">
          <h1 className="text-2xl font-bold">{result.member.name}</h1>
          <div className="mt-2">
            <StatusBadge estado={result.status} />
          </div>
        </div>

        {/* Dynamic QR */}
        <div className="p-6 flex flex-col items-center">
          <div className="bg-white border-4 border-gray-100 rounded-xl p-3">
            <img
              src={clubsApi.verifyQrUrl(params.token)}
              alt="QR de verificación"
              className="w-52 h-52"
            />
          </div>
          <p className="text-xs text-gray-400 mt-3 text-center">
            Muestra este QR en la puerta. La vigencia se consulta en vivo:
            si tu membresía cambia, el veredicto cambia al instante.
          </p>
        </div>

        <div className="bg-gray-50 px-6 py-3 text-center text-xs text-gray-400">
          Verificado por Akitoi · {new Date(result.checked_at).toLocaleString()}
        </div>
      </div>
      <p className="text-xs text-gray-400 mt-4">
        Consejo: guarda esta página o haz captura para llevarla contigo.
      </p>
    </Shell>
  )
}

function Shell({ children }: { children: React.ReactNode }) {
  return (
    <main className="min-h-screen bg-gray-100 flex flex-col items-center justify-center px-4 py-10">
      {children}
    </main>
  )
}
