/** @type {import('next').NextConfig} */
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost'],
  },
  // VISTA 3: al escanear un carnet, /verify/{token} en el dominio del
  // frontend sirve la página de veredicto a color que ya renderiza el
  // backend (verde/rojo/ámbar) — no se reconstruye en Next.
  async rewrites() {
    return [
      {
        source: '/verify/:token*',
        destination: `${API_URL}/verify/:token*`,
      },
    ]
  },
}

module.exports = nextConfig
