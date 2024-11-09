import vue from '@vitejs/plugin-vue'
import {fileURLToPath, URL} from 'node:url'
import {defineConfig} from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
  resolve: {
    alias: {'@': fileURLToPath(new URL('./src', import.meta.url))},
  },
  plugins: [vue()],
  server: {host: '0.0.0.0', port: '5999'}
})
