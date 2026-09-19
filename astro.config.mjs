// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  // Site servi à la racine d'une GitHub Pages "user site"
  // (repo NicolasSCH2ER.github.io) → pas de `base` à propager dans les liens.
  site: 'https://nicolassch2er.github.io',
  integrations: [sitemap()],
});
