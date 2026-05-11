import PocketBase from 'pocketbase';
import type { Locale } from '~/i18n/utils';

const PB_URL = import.meta.env.PB_URL ?? 'https://pb.binarywd.com';

export const pb = new PocketBase(PB_URL);

/**
 * Safe wrapper — если PB не отвечает / коллекция пуста, возвращает fallback.
 * Это держит билд зелёным даже когда сервер лёг.
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

// ── singleton-getter helper ─────────────────────────────────────────
async function getSingleton(name: string, lang: Locale) {
  return safeFetch(
    () => pb.collection(name).getFirstListItem(`lang="${lang}"`) as Promise<any>,
    null as any,
  );
}

// ── public readers ──────────────────────────────────────────────────

export async function getGlobals(lang: Locale = 'ru') {
  return getSingleton('globals', lang);
}

export async function getPageIndex(lang: Locale = 'ru') {
  return getSingleton('page_index', lang);
}

export async function getPageAbout(lang: Locale = 'ru') {
  return getSingleton('page_about', lang);
}

export async function getServices(lang: Locale = 'ru') {
  return safeFetch(
    () => pb.collection('services').getFullList({
      sort: 'order',
      filter: `lang="${lang}"`,
    }) as Promise<any[]>,
    [] as any[],
  );
}

export async function getDispatch(lang: Locale = 'ru', limit = 10) {
  return safeFetch(
    () => pb.collection('dispatch').getFullList({
      sort: '-published_at',
      filter: `lang="${lang}"`,
    }).then(rows => rows.slice(0, limit)) as Promise<any[]>,
    [] as any[],
  );
}

export async function getTeam(lang: Locale = 'ru') {
  return safeFetch(
    () => pb.collection('team').getFullList({
      sort: 'order',
      filter: `lang="${lang}"`,
    }) as Promise<any[]>,
    [] as any[],
  );
}

import { cases as fixtureCases } from './fixtures';

export async function getCases(lang: Locale = 'ru') {
  return safeFetch(
    () => pb.collection('cases').getFullList({
      sort: '-year,-created',
      filter: `lang="${lang}"`,
    }) as Promise<any[]>,
    fixtureCases as any[],
  );
}

export async function getCase(slug: string, lang: Locale = 'ru') {
  return safeFetch(
    () => pb.collection('cases').getFirstListItem(`slug="${slug}" && lang="${lang}"`) as Promise<any>,
    null,
  );
}

// ── form submission ─────────────────────────────────────────────────

export type BriefPayload = {
  name: string;
  contact: string;
  company?: string;
  services?: string[];
  budget?: string;
  story: string;
  source?: string;
  lang?: Locale;
};

/**
 * Создаёт запись в `briefs`. Публичный POST (createRule = "" в PB),
 * поэтому не требует токена. Используется со страницы формы.
 */
export async function submitBrief(payload: BriefPayload) {
  return pb.collection('briefs').create({
    ...payload,
    status: 'new',
    source: payload.source ?? (typeof window !== 'undefined' ? window.location.pathname : ''),
    user_agent: typeof navigator !== 'undefined' ? navigator.userAgent : '',
  });
}
