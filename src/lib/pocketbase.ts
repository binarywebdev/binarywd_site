import PocketBase from 'pocketbase';

const PB_URL = import.meta.env.PB_URL ?? 'http://127.0.0.1:8090';

export const pb = new PocketBase(PB_URL);

/**
 * Safe wrapper — если PB не поднят, возвращает fallback вместо падения сборки.
 * Так локально можно работать без запущенного PocketBase, используя моки в src/lib/fixtures.ts.
 */
export async function safeFetch<T>(fn: () => Promise<T>, fallback: T): Promise<T> {
  try {
    return await fn();
  } catch (err) {
    if (import.meta.env.DEV) {
      console.warn('[pocketbase] fallback used:', (err as Error)?.message);
    }
    return fallback;
  }
}

// ── Активные читалки из PB ────────────────────────────────────────────────
// Если PB лёг/коллекция пуста — safeFetch вернёт fallback (статичные моки из
// fixtures.ts), сайт не сломается на билде.

import { cases as fixtureCases } from './fixtures';

export async function getCases(lang: 'ru' | 'en' = 'ru') {
  return safeFetch(
    () => pb.collection('cases').getFullList({
      sort: '-year,-created',
      filter: `lang="${lang}"`,
    }) as Promise<any[]>,
    fixtureCases as any[],
  );
}

export async function getCase(slug: string, lang: 'ru' | 'en' = 'ru') {
  return safeFetch(
    () => pb.collection('cases').getFirstListItem(`slug="${slug}" && lang="${lang}"`) as Promise<any>,
    null,
  );
}
