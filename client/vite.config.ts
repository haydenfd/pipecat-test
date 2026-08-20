import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const botPort = process.env.BOT_PORT || '1212';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5100,
    proxy: {
      '/api': `http://127.0.0.1:${botPort}`,
    },
  },
});
