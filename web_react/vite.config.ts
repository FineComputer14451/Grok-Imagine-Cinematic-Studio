import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const apiTarget = process.env.VITE_API_PROXY_TARGET || 'http://127.0.0.1:8090'

const studioApiProxy = {
  // Vite → studio_api (cinematic-studio api --port 8090)
  '/v1': {
    target: apiTarget,
    changeOrigin: true,
  },
  '/health': {
    target: apiTarget,
    changeOrigin: true,
  },
}

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: studioApiProxy,
  },
  preview: {
    port: 4173,
    proxy: studioApiProxy,
  },
})
