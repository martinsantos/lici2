import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  
  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      port: 3000,
      cors: true,
      proxy: {
        '/api/v1/documents': {
          target: env.VITE_API_BASE_URL || 'http://localhost:4322',
          changeOrigin: true,
          secure: false,
          configure: (proxy, _options) => {
            proxy.on('error', (err, _req, _res) => {
              console.log('proxy error for documents:', err);
            });
          }
        },
        '/api/v1/licitaciones': {
          target: env.VITE_API_BASE_URL || 'http://localhost:4322',
          changeOrigin: true,
          secure: false,
          configure: (proxy, _options) => {
            proxy.on('error', (err, _req, _res) => {
              console.log('proxy error for licitaciones:', err);
            });
          }
        }
      }
    },
    define: {
      'import.meta.env.VITE_API_BASE_URL': JSON.stringify(env.VITE_API_BASE_URL),
      'import.meta.env.VITE_API_TIMEOUT': env.VITE_API_TIMEOUT || '30000',
    }
  };
});
