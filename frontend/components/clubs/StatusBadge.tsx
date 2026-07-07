import { MemberEstado } from '@/lib/api'

const STYLES: Record<MemberEstado, string> = {
  vigente: 'bg-green-100 text-green-800 border-green-300',
  suspendido: 'bg-red-100 text-red-800 border-red-300',
  vencido: 'bg-amber-100 text-amber-800 border-amber-300',
  baja: 'bg-gray-200 text-gray-600 border-gray-300',
}

export default function StatusBadge({ estado }: { estado: MemberEstado }) {
  return (
    <span
      className={`inline-block px-3 py-1 rounded-full text-xs font-semibold border uppercase tracking-wide ${
        STYLES[estado] || STYLES.baja
      }`}
    >
      {estado}
    </span>
  )
}
