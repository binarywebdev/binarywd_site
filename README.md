# impuls / studio — Astro + PocketBase

Studio website. Vanilla Astro (без React/Vue), built-in i18n (RU/EN), контент позднее переедет в PocketBase.

## Стек

- **Astro 4** — статический генератор, шаблоны в `.astro` (HTML + frontmatter + scoped CSS).
- **PocketBase** — Go-бинарник с админкой и SQLite, для управления контентом. Подключён через `pocketbase` JS SDK.
- **Шрифты:** Instrument Serif + JetBrains Mono + Inter (через Google Fonts CDN).
- Нет React/Vue/Svelte интеграций — только нативные Astro-компоненты.

## Локальная разработка

```bash
# 1. Установить зависимости
npm install

# 2. Запустить dev-сервер (по умолчанию http://localhost:4321)
npm run dev

# 3. Билд для прода
npm run build

# 4. Превью билда
npm run preview
```

## Структура

```
src/
├── layouts/        — общий каркас (Layout.astro)
├── components/     — Nav, Footer, StickyCta
├── views/          — IndexView, WorkView, CaseView, AboutView
│                     (вся вёрстка страниц, без привязки к языку)
├── pages/          — тонкие обёртки роутов (RU по умолчанию)
│   ├── index.astro
│   ├── about.astro
│   ├── work/
│   │   ├── index.astro
│   │   └── [slug].astro       — динамические кейсы
│   └── en/                    — те же роуты для EN под /en/...
├── i18n/           — словари ru.json/en.json + утилита t()
├── lib/
│   ├── pocketbase.ts          — клиент PB + safeFetch
│   └── fixtures.ts            — моки коллекций (cases, dispatch) пока PB не поднят
└── styles/
    └── global.css             — токены, базовый сброс, общие keyframes
```

## i18n

Используется встроенный `astro:i18n` (Astro 4+):

- defaultLocale: `ru` → URL `/` (без префикса)
- locales: `ru`, `en` → URL `/en/...`
- В шаблонах: `t(lang, 'hero.titleA')` + `localePath(lang, '/work')`
- Свитчер в `Nav.astro` показывает противоположный язык в правом углу

Добавить третий язык: положить `src/i18n/xx.json`, добавить в `astro.config.mjs` → `locales`, продублировать пары роутов в `src/pages/xx/...`.

## PocketBase

### Сейчас (без PB)
- `src/lib/fixtures.ts` отдаёт мок-данные (3 кейса, 3 dispatch-поста).
- Views рендерятся в статику. Билд проходит даже без запущенного PB.

### Когда поднимем PB
1. Скачать бинарник: https://pocketbase.io/docs/
2. Положить рядом (gitignore уже исключает `pb_data/` и сам бинарник).
3. Запустить: `./pocketbase serve` → админка на http://127.0.0.1:8090/_/
4. Создать `.env` из `.env.example`, прописать `PB_URL`.
5. В `src/lib/pocketbase.ts` раскомментировать `getCases`, `getDispatch` и т.д.
6. В views поменять `import { cases } from '~/lib/fixtures'` на `await getCases(lang)`.

### Планируемые коллекции PB
- `cases` — slug, title, sub, tags[], year, status, category, body_blocks(json), cover(file), gallery(files[]), client, services[], stack[], stats{turnover,speedup,live_count,latency_ms}, quote{text,author}, lang
- `dispatch` — slug, title, excerpt, body(rich), tags[], published_at, pinned(bool), read_time, lang
- `team` — name, role, bio, avatar, links[], order
- `globals` — singleton: ticker_items, offices, social_links, manifesto_rules

Все локализуемые сущности дублируются строкой по `lang` или храним переводы в jsonb-полях — определимся при создании схемы.

## Деплой

- `npm run build` собирает в `dist/` чистую статику.
- Деплой = синхронизация `dist/` на хостинг (любой статик-хост: Nginx, Caddy, Vercel, Cloudflare Pages).
- Для авто-ребилда при изменении контента в PB: webhook → CI → `npm run build` → деплой.

## Reference

Исходные HTML-прототипы лежат в `_design-reference/` — это вёрстка, с которой портировались Astro-шаблоны. Можно сравнивать и обновлять оба, пока структура не стабилизируется.
