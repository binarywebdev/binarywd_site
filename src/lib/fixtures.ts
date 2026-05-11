/**
 * Локальные моки — пока PocketBase не поднят и коллекции пустые.
 * Те же поля, что и в будущих PB-коллекциях, чтобы переход был чистым.
 */

export type CaseRow = {
  slug: string;
  title: string;
  sub: string;
  tags: string[];
  meta: string[];
  year: string;
  status: 'live' | 'case' | 'nda' | 'archive';
  category: string;
};

export type DispatchPost = {
  date: { day: string; full: string };
  title: string;
  excerpt: string;
  tags: { label: string; kind?: 'pin' | 'live' | 'default' }[];
  read: string;
};

export const cases: CaseRow[] = [
  {
    slug: 'impuls-bot',
    title: 'Impuls-bot v2',
    sub: 'auto-trading platform with backtest engine',
    tags: ['trading · infra', 'fastapi · react', 'binance · bybit'],
    meta: ['fastapi', 'react', 'binance'],
    year: "'26",
    status: 'live',
    category: 'trading'
  },
  {
    slug: 'parabolic',
    title: 'Parabolic',
    sub: 'identity for a quant fund — numbers as poetry',
    tags: ['brand', 'logo · system', 'guidelines'],
    meta: ['brand'],
    year: "'25",
    status: 'case',
    category: 'brand'
  },
  {
    slug: 'coldstack',
    title: 'Coldstack',
    sub: 'web3 storage protocol launch site',
    tags: ['landing', 'next · framer', 'shader hero'],
    meta: ['landing'],
    year: "'25",
    status: 'live',
    category: 'landing'
  },
  {
    slug: 'orderflow',
    title: 'Orderflow',
    sub: 'realtime tape reader for a prop desk',
    tags: ['trading · ui', 'react · canvas', '200 ws streams'],
    meta: ['trading'],
    year: "'25",
    status: 'nda',
    category: 'trading'
  },
  {
    slug: 'hedge-ui',
    title: 'Hedge.ui',
    sub: 'hedging terminal — 200 instruments, one screen',
    tags: ['trading · ui', 'react · websocket', 'naked check'],
    meta: ['trading'],
    year: "'25",
    status: 'live',
    category: 'trading'
  },
  {
    slug: 'mint-fm',
    title: 'Mint.fm',
    sub: 'curated NFT drop platform — zero fees',
    tags: ['product · brand', 'full identity', 'marketplace'],
    meta: ['brand'],
    year: "'25",
    status: 'archive',
    category: 'brand'
  }
];

export const dispatch: DispatchPost[] = [
  {
    date: { day: '11 / 05', full: '2026 · 14:32 UTC' },
    title: 'Impuls-bot v2.6 — confirmation signals & second-impulse entry',
    excerpt:
      'Релиз бэктеста с подтверждением сигнала: алёрт + повторный импульс в окне с правилом направления и min-rank. Меньше ложных входов на боковике, лучше hit-rate на трендах.',
    tags: [
      { label: 'pinned', kind: 'pin' },
      { label: 'release' },
      { label: 'v2.6' }
    ],
    read: '→ read 4 min'
  },
  {
    date: { day: '09 / 05', full: '2026 · 09:11 UTC' },
    title: 'Починили парсинг robots.params — бот наконец-то торгует тем, что вы ему написали',
    excerpt:
      'Старый баг: TEXT-поле параметров не парсилось, форма редактирования робота показывала дефолты. Бот при этом использовал устаревшие значения. Аудит + миграция + жёсткая типизация.',
    tags: [
      { label: 'live fix', kind: 'live' },
      { label: 'product' }
    ],
    read: '→ read 6 min'
  },
  {
    date: { day: '03 / 05', full: '2026 · 17:00 UTC' },
    title: 'Hedge terminal — 200 инструментов на одном экране',
    excerpt:
      'Запустили в проде хеджирующий терминал для прайвет-клиента: realtime mark-price, naked check, авто-reconcile с биржей.',
    tags: [{ label: 'product' }, { label: 'case-study' }],
    read: '→ read 8 min'
  }
];
