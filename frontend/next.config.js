/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Configuração da API URL via variável de ambiente
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080',
  },
  // Configurações adicionais
  experimental: {
    // Next.js 15 features
  },
}

module.exports = nextConfig
