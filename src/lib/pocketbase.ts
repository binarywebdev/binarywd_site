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

// ── Future shape (когда PB поднимется и коллекции созданы) ─────────────────
//
// export async function getCases(lang: 'ru' | 'en') {
//   return safeFetch(
//     () => pb.collection('cases').getFullList({ sort: '-year,-created', filter: `lang="${lang}"` }),
//     []
//   );
// }
//
// export async function getCase(slug: string, lang: 'ru' | 'en') {
//   return safeFetch(
//     () => pb.collection('cases').getFirstListItem(`slug="${slug}" && lang="${lang}"`),
//     null
//   );
// }
//
// export async function getDispatch(lang: 'ru' | 'en') {
//   return safeFetch(
//     () => pb.collection('dispatch').getFullList({ sort: '-published_at', filter: `lang="${lang}"` }),
//     []
//   );
// }
