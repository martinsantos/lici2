import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import node from '@astrojs/node';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  integrations: [
    tailwind(),
    react()
  ],
  output: 'server',
  adapter: node({
    mode: 'standalone'
  }),
  vite: {
    ssr: {
      noExternal: ['@mui/material', '@mui/icons-material', '@emotion/react', '@emotion/styled']
    }
  },
  server: {
    port: 3002,
    host: true
  }
});
