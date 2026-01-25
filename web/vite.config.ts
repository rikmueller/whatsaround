/// <reference types="node" />
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import dotenv from 'dotenv'
import { resolve } from 'path'

// Load config/.env (shared) and optional web/.env.local overrides
const configEnv = dotenv.config({ path: resolve(__dirname, '../config/.env') }).parsed || {}
const localEnv = dotenv.config({ path: resolve(__dirname, '.env.local') }).parsed || {}

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
  const env = { ...configEnv, ...viteEnv, ...localEnv, ...process.env }

  const allowedHosts = parseHosts(env.VITE_ALLOWED_HOSTS || env.ALONGGPX_HOSTNAME) || ['.']
  const hmrHost = env.ALONGGPX_HOSTNAME || env.VITE_HMR_HOST
  const clientEnv = buildClientEnv(env as Record<string, string>)

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
          target: 'http://localhost:5000',
          changeOrigin: true,
          rewrite: (path) => path,
        },
      },
    },
    build: {
      outDir: 'dist',
      sourcemap: false,
    },
  }
})
