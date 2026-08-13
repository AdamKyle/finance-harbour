import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vite';

const dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    allowedHosts: ['finance-harbour.test'],
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: false,
        secure: false,
        xfwd: true,
        headers: {
          'X-Forwarded-Proto': 'https',
        },
      },
    },
    watch: {
      usePolling: true,
    },
  },
  resolve: {
    alias: {
      assets: path.resolve(dirname, 'src/assets'),
      components: path.resolve(dirname, 'src/components'),
      layout: path.resolve(dirname, 'src/layout'),
      pages: path.resolve(dirname, 'src/pages'),
      router: path.resolve(dirname, 'src/react-router'),
      styles: path.resolve(dirname, 'src/styles'),
      ui: path.resolve(dirname, 'src/ui'),
      configuration: path.resolve(dirname, 'src/configuration'),
      lib: path.resolve(dirname, 'src/lib'),
      util: path.resolve(dirname, 'src/util'),
    },
  },
});
