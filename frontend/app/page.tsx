import Link from 'next/link'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-center font-mono text-sm flex flex-col gap-8">
        <h1 className="text-4xl font-bold text-center">
          Bienvenido a Akitoi
        </h1>
        <p className="text-xl text-center text-gray-600">
          Tu hub de contacto profesional en un solo lugar
        </p>
        <div className="flex gap-4">
          <Link
            href="/juan-tello"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Ver perfil de ejemplo
          </Link>
        </div>
      </div>
    </main>
  )
}
