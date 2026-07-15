// @ts-check
import { defineConfig } from 'astro/config';

import react from '@astrojs/react';
import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  site: "https://jaimenguyen168.github.io",
  base: "/wat-claude-job-applykit",
  integrations: [react()],

  vite: {
    plugins: [tailwindcss()]
  }
});