/// <reference types="node" />
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import dotenv from 'dotenv'
import { resolve } from 'path'

// Load config/local-dev/.env for local development configuration
const localDevEnv = dotenv.config({ path: resolve(__dirname, '..', 'config', 'local-dev', '.env') }).parsed || {}
// Load frontend/.env.local for personal overrides (highest priority)
const personalEnv = dotenv.config({ path: resolve(__dirname, '.env.local') }).parsed || {}

const parseHosts = (value?: string) =>
  value
    ? value
        .replace(/;/g, ',')
        .split(',')
        .map((item) => item.trim())
        .filter(Boolean)
    : null

const buildClientEnv = (vars: Record<string, string>) => {
  const out: Record<string, string> = {}
  for (const [key, value] of Object.entries(vars)) {
    if (key.startsWith('VITE_')) {
      out[`import.meta.env.${key}`] = JSON.stringify(value)
    }
    if (key.startsWith('ALONGGPX_')) {
      out[`import.meta.env.VITE_${key}`] = JSON.stringify(value)
    }
  }
  return out
}

export default defineConfig(({ mode }) => {
  const viteEnv = loadEnv(mode, process.cwd(), '')
  const env = { ...localDevEnv, ...viteEnv, ...personalEnv, ...process.env }

  const allowedHosts = parseHosts(env.VITE_ALLOWED_HOSTS || env.ALONGGPX_HOSTNAME) || ['.']
  const hmrHost = env.ALONGGPX_HOSTNAME || env.VITE_HMR_HOST
  const clientEnv = buildClientEnv(env as Record<string, string>)
  
  // Use environment variable for backend URL (Docker uses service name, local uses localhost)
  const backendTarget = env.VITE_BACKEND_URL || 'http://localhost:5000'

  return {
    plugins: [react()],
    define: clientEnv,
    server: {
      host: '0.0.0.0',
      port: 3000,
      allowedHosts,
      ...(hmrHost && {
        hmr: {
          host: hmrHost,
          protocol: 'ws',
        },
      }),
      proxy: {
        '/api': {
          target: backendTarget,
          changeOrigin: true,
          rewrite: (path) => path,
        },
        '/socket.io': {
          target: backendTarget,
          changeOrigin: true,
          ws: false,  // Disable WebSocket upgrade, use polling only
        },
      },
    },
    build: {
      outDir: 'dist',
      sourcemap: false,
    },
  }
})
