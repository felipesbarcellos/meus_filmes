import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path' // Adicionar a importação do módulo path

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: { // Adicionar a configuração de resolve
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  // server: {
  //   allowedHosts: ['my-frontend.local'],
  // },
})
