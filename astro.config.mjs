import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://binarywd.local',
  i18n: {
    defaultLocale: 'ru',
    locales: ['ru', 'en'],
    routing: {
      prefixDefaultLocale: false
    }
  },
  server: {
    port: 4321,
    host: true
  }
});
