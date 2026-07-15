// @ts-check
import { defineConfig } from 'astro/config';

import react from '@astrojs/react';
import tailwindcss from '@tailwindcss/vite';

const isProd = process.env.NODE_ENV === "production";

// https://astro.build/config
export default defineConfig({
  site: "https://jaimenguyen168.github.io",
  base: isProd ? "/wat-claude-job-applykit" : "/",
  integrations: [react()],

  vite: {
    plugins: [tailwindcss()]
  }
});