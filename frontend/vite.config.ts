import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    tailwindcss(),
    react(),
  ],
  server: {
    port: 5173,
    proxy: {
      // 前端所有 /api/* 请求代理到 FastAPI:8000
      // 例：/api/chat → http://localhost:8000/chat
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      // 图片静态文件代理：/images/* → FastAPI:8000/images/*
      '/images': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
