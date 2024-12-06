import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3002,
    proxy: {
      '/api/v1': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
        ws: true
      }
    }
  },
  optimizeDeps: {
    include: [
      '@astrojs/react/client',
      'react',
      'react-dom',
      'react-router-dom',
      'react-hot-toast',
      '@astrojs/client',
      'astro/runtime/client',
      'astro/runtime/client/dev-toolbar',
      '@astrojs/aria-query',
      '@astrojs/axobject-query'
    ],
    force: true,
    esbuildOptions: {
      target: 'es2020'
    }
  },
  build: {
    target: 'es2020',
    rollupOptions: {
      external: ['astro:content']
    }
  },
  resolve: {
    alias: {
      '@components': '/src/components',
      '@layouts': '/src/layouts',
      '@styles': '/src/styles'
    }
  }
});
