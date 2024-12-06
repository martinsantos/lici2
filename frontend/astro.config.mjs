import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  integrations: [
    react(),
    tailwind(),
  ],
  output: 'hybrid',
  server: {
    port: 3000,
  },
  vite: {
    ssr: {
      noExternal: ['@radix-ui/*'],
    },
  },
});
