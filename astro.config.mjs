// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  // Site servi à la racine d'une GitHub Pages "user site"
  // (repo NicolasSCH2ER.github.io) → pas de `base` à propager dans les liens.
  site: 'https://nicolassch2er.github.io',
  // FR par défaut, non préfixé (routes existantes inchangées) ; EN sous /en/.
  i18n: {
    locales: ['fr', 'en'],
    defaultLocale: 'fr',
    routing: { prefixDefaultLocale: false },
  },
  integrations: [
    sitemap({
      i18n: {
        defaultLocale: 'fr',
        locales: { fr: 'fr-FR', en: 'en-US' },
      },
    }),
  ],
});
