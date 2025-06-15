import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import svgr from "vite-plugin-svgr"


export default defineConfig({
  plugins: [react(), 
    svgr({ exportAsDefault: false })
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    proxy: {
      '/create_user': 'http://localhost:8000',
      '/login': 'http://localhost:8000',
      '/available_courses': 'http://localhost:8000',
      '/get_course_info': 'http://localhost:8000',
      '/create_course': 'http://localhost:8000',
    },
  },
})
