import vue from '@vitejs/plugin-vue'
import {fileURLToPath, URL} from 'node:url'
import {defineConfig} from 'vite'

export default defineConfig({
  resolve: {
    alias: {'@': fileURLToPath(new URL('./src', import.meta.url))},
  },
  base: './',
  plugins: [vue()],
  server: {host: 'localhost', port: '5999'}
})
