import ru from './ru.json';
import en from './en.json';

export type Locale = 'ru' | 'en';

const dicts: Record<Locale, any> = { ru, en };

/**
 * Translate by dot-path key. Falls back to the key string if missing.
 * Usage: t(lang, 'hero.titleA')
 */
export function t(lang: Locale, key: string): any {
  const parts = key.split('.');
  let cur: any = dicts[lang] ?? dicts.ru;
  for (const p of parts) {
    if (cur == null) return key;
    cur = cur[p];
  }
  return cur ?? key;
}

/**
 * Get a path under the given locale (prefixed only for non-default).
 * default locale (ru) → "/foo"; "en" → "/en/foo".
 */
export function localePath(lang: Locale, path: string): string {
  const clean = path.startsWith('/') ? path : '/' + path;
  if (lang === 'ru') return clean;
  return '/en' + (clean === '/' ? '' : clean);
}

/**
 * The "other" locale link for the language switcher.
 */
export function otherLocale(lang: Locale): Locale {
  return lang === 'ru' ? 'en' : 'ru';
}
