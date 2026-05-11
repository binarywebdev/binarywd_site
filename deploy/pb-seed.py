#!/usr/bin/env python3
"""
Идемпотентный сид-скрипт для PocketBase.

Берёт контент из src/i18n/{ru,en}.json и src/lib/fixtures.ts и пушит в PB.
Если запись с таким (lang) / (slug, lang) уже есть — обновляет.
Если нет — создаёт.

Запуск:
    python deploy/pb-seed.py \
      --pb https://pb.binarywd.com \
      --email hello.chat@binarywd.com \
      --password '<пароль>'
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


# ── helpers ─────────────────────────────────────────────────────────

def http(method, url, body=None, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    data = json.dumps(body, ensure_ascii=False).encode('utf-8') if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read().decode() or '{}')
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or '{}')


def login(pb, email, password):
    code, data = http('POST', f'{pb}/api/admins/auth-with-password',
                      {'identity': email, 'password': password})
    if code != 200 or 'token' not in data:
        sys.exit(f'auth failed: {code} {data}')
    print('[auth] OK')
    return data['token']


def upsert(pb, token, collection, find_filter, payload):
    """Найти по фильтру → обновить, иначе создать."""
    code, data = http(
        'GET',
        f'{pb}/api/collections/{collection}/records?filter={urllib.parse.quote(find_filter)}&perPage=1',
        token=token,
    )
    if code != 200:
        print(f'  [find] FAIL {collection} ({find_filter}): {code} {data}')
        return
    items = data.get('items', [])
    if items:
        rec_id = items[0]['id']
        code, data = http('PATCH', f'{pb}/api/collections/{collection}/records/{rec_id}',
                          payload, token=token)
        if code == 200:
            print(f'  [up]  ~ {collection} {find_filter}')
        else:
            print(f'  [up]  X {collection} {find_filter} -> {code} {data}')
    else:
        code, data = http('POST', f'{pb}/api/collections/{collection}/records',
                          payload, token=token)
        if code in (200, 204):
            print(f'  [new] + {collection} {find_filter}')
        else:
            print(f'  [new] X {collection} {find_filter} -> {code} {data}')


# ── data sources ────────────────────────────────────────────────────

def load_i18n(lang):
    p = ROOT / 'src' / 'i18n' / f'{lang}.json'
    return json.loads(p.read_text(encoding='utf-8'))


# простой парсер fixtures.ts через регулярки: вытащим массив cases
def load_fixtures_cases():
    text = (ROOT / 'src' / 'lib' / 'fixtures.ts').read_text(encoding='utf-8')
    # Найти `export const cases: CaseRow[] = [ ... ];`
    m = re.search(r'export const cases[^=]*=\s*\[(.*?)\];', text, re.S)
    if not m:
        return []
    blob = '[' + m.group(1) + ']'
    # Превратить TS-литералы в JSON: ключи без кавычек → с кавычками; одинарные → двойные;
    # хвостовые запятые убрать.
    blob = re.sub(r"([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:", r'\1"\2":', blob)
    blob = blob.replace("'", '"')
    blob = re.sub(r",(\s*[\]}])", r"\1", blob)
    return json.loads(blob)


def load_fixtures_dispatch():
    text = (ROOT / 'src' / 'lib' / 'fixtures.ts').read_text(encoding='utf-8')
    m = re.search(r'export const dispatch[^=]*=\s*\[(.*?)\];', text, re.S)
    if not m:
        return []
    blob = '[' + m.group(1) + ']'
    blob = re.sub(r"([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:", r'\1"\2":', blob)
    blob = blob.replace("'", '"')
    blob = re.sub(r",(\s*[\]}])", r"\1", blob)
    return json.loads(blob)


# ── seeders ─────────────────────────────────────────────────────────

SEO_DEFAULTS = {
    'ru': {
        'site_name': 'impuls / studio',
        'description': 'Crypto-native студия дизайна и разработки. Терминалы, бот-инфраструктура, лендинги под токен-лонч.',
        'og_image': '/og/default.png',
        'twitter_handle': '@impuls_studio',
        'theme_color': '#0a0a0a',
        'keywords': 'crypto, web3, trading ui, дизайн-студия, бот, fastapi, react',
    },
    'en': {
        'site_name': 'impuls / studio',
        'description': 'Crypto-native design + development studio. Trading terminals, bot infrastructure, token-launch landings.',
        'og_image': '/og/default.png',
        'twitter_handle': '@impuls_studio',
        'theme_color': '#0a0a0a',
        'keywords': 'crypto, web3, trading ui, design studio, bot, fastapi, react',
    },
}

FOOTER_MISC = {
    'ru': {
        'telegram_label': 'telegram', 'response_label': 'response',
        'pdf_label': 'PDF', 'mark': 'impuls / studio',
    },
    'en': {
        'telegram_label': 'telegram', 'response_label': 'response',
        'pdf_label': 'PDF', 'mark': 'impuls / studio',
    },
}


def seed_globals(pb, token):
    print('[globals]')
    for lang in ('ru', 'en'):
        d = load_i18n(lang)
        payload = {
            'lang': lang,
            'nav_labels': d.get('nav', {}),
            'manifest_rules': d.get('manifest', {}).get('rules', []),
            'ticker_items': [
                {'text': 'BTC', 'value': '$67,420', 'kind': 'up', 'delta': '+2.41%'},
                {'text': 'ETH', 'value': '$3,812',  'kind': 'up', 'delta': '+1.08%'},
                {'text': 'SOL', 'value': '$184.20', 'kind': 'dn', 'delta': '-0.74%'},
                {'text': 'STUDIO STATUS', 'value': 'ACCEPTING Q3 / 2026', 'kind': 'up'},
                {'text': 'LOCATION', 'value': 'REMOTE · UTC+3'},
            ],
            'offices': list(d.get('footer', {}).get('offices', {}).values()),
            'social_links': [
                {'key': 'x',  'label': 'x',  'url': '#'},
                {'key': 'dr', 'label': 'dr', 'url': '#'},
                {'key': 'gh', 'label': 'gh', 'url': '#'},
                {'key': 'tg', 'label': 'tg', 'url': '#'},
                {'key': 'cv', 'label': 'cv', 'url': '#'},
            ],
            'footer_talk': {
                'talk':     d.get('footer', {}).get('talk'),
                'talkEm':   d.get('footer', {}).get('talkEm'),
                'studio':   d.get('footer', {}).get('studio'),
                'practice': d.get('footer', {}).get('practice'),
                'contact':  d.get('footer', {}).get('contact'),
                'links':    d.get('footer', {}).get('links', {}),
                'copy':     d.get('footer', {}).get('copy'),
            },
            'legal': d.get('footer', {}).get('legal', {}),
            'seo_defaults':     SEO_DEFAULTS[lang],
            'footer_misc':      FOOTER_MISC[lang],
            'contact_email':    'hi@impuls.studio',
            'contact_telegram': '@impuls_studio',
            'response_sla':     '< 24h',
            'version':          'v 0.1.0 · astro + pb',
        }
        upsert(pb, token, 'globals', f'lang="{lang}"', payload)


def seed_page_index(pb, token):
    print('[page_index]')
    for lang in ('ru', 'en'):
        d = load_i18n(lang)
        work = d.get('work', {})
        payload = {
            'lang': lang,
            'hero': d.get('hero', {}),
            'services': d.get('services', {}),
            'manifest': d.get('manifest', {}),
            'marquee': ['Trading UI', '· Token Launchpads', '· Bot Dashboards',
                        '· Wallet UX', '· DeFi Frontends', '· Market Sites'],
            'contact_form': d.get('contact', {}),
            'dispatch': d.get('dispatch', {}),
            'work': {
                'title': work.get('headTitle'),
                'em':    work.get('headEm'),
                'link':  work.get('headMeta'),
                'page': {
                    'archive_total': 17,
                    'nda_hidden':    5,
                    'span':          '2024 — 2026',
                    'slots':         'Q3 / 2026',
                    'archive_label':       'archive' if lang == 'ru' else 'archive',
                    'span_label':          'span'    if lang == 'ru' else 'span',
                    'filter_label':        'filter by tag / year / status' if lang == 'ru' else 'filter by tag / year / status',
                    'nda_label':           'under NDA' if lang == 'ru' else 'under NDA',
                    'live_products':       'live products' if lang == 'ru' else 'live products',
                    'next_slots':          'next slots' if lang == 'ru' else 'next slots',
                    'filters_categories':  [
                        {'key': 'all',     'label': 'all'},
                        {'key': 'trading', 'label': 'trading'},
                        {'key': 'brand',   'label': 'brand'},
                        {'key': 'landing', 'label': 'landing'},
                    ],
                    'sort_label':   'sort / recent' if lang == 'ru' else 'sort / recent',
                    'end_title':    work.get('endTitle'),
                    'end_em':       'similar',
                    'end_text':     work.get('endText'),
                    'cta_label':    'start a project',
                    'seo': {
                        'title':       'Работы · impuls / studio' if lang == 'ru' else 'Work · impuls / studio',
                        'description': 'Портфолио студии: trading-UI, бот-инфра, лендинги и брендинг для крипто-команд.' if lang == 'ru'
                                       else 'Studio portfolio: trading UI, bot infra, landings and branding for crypto teams.',
                        'canonical_path': '/work' if lang == 'ru' else '/en/work',
                    },
                },
            },
            'seo': {
                'title': 'impuls / studio — crypto-native design + dev',
                'description': 'Студия дизайна и разработки криптопродуктов: терминалы, бот-инфра, лендинги.' if lang == 'ru' else 'Crypto-native design + dev studio: terminals, bot infra, token landings.',
                'canonical_path': '/' if lang == 'ru' else '/en/',
                'keywords': 'crypto, web3, trading, fastapi, react',
            },
        }
        upsert(pb, token, 'page_index', f'lang="{lang}"', payload)


def seed_page_about(pb, token):
    print('[page_about]')
    base = {
        'ru': {
            'hero': {
                'title_lines': [
                    {'plain': "we're "}, {'em': 'three'}, {'plain': ' people'},
                    {'plain': 'who got '}, {'strike': 'tired'}, {'em': 'obsessed'},
                    {'plain': 'with crypto '}, {'em': 'UI'},
                ],
                'lede': 'impuls / studio — небольшая независимая команда: trader, designer & engineer.',
                'lede_rest': 'Делаем продукты для тех, кто работает на рынке каждый день: терминалы, бот-инфра, лендинги под токен-лонч.',
                'meta': [
                    {'k': 'founded', 'v': '2024'},
                    {'k': 'headcount', 'v': '3 + 2 freelance'},
                    {'k': 'location', 'v': 'remote · UTC+3'},
                    {'k': 'status', 'v': '● accepting Q3 / 2026', 'accent': True},
                ],
            },
            'nums': [
                {'v': '<em>17</em>', 'k': 'shipped projects'},
                {'v': '2<em>.5</em>', 'k': 'years live'},
                {'v': '<em>$3M</em><sup>+</sup>', 'k': 'turnover on our products'},
                {'v': '12', 'k': 'live in production'},
                {'v': '<em>0</em>', 'k': 'stock 3D blobs used'},
            ],
            'story': {
                'tag': '[ 01 ] / story',
                'h2': 'как мы тут <em>оказались</em>.',
                'big': 'Мы начали со своей боли. <em>Трейдили</em> сами — и каждый раз бесили интерфейсы, в которых критическая цифра спрятана под аккордеоном.',
                'p': 'В 2024 собрали первый внутренний инструмент — бот с админкой для управления стратегией. Через месяц нас попросили сделать «то же самое, но для друга». Через три — пришёл первый платный проект.',
            },
            'final_meta': 'or write directly · <b>hi@impuls.studio</b> · <b>@impuls_studio</b>',
        },
        'en': {
            'hero': {
                'title_lines': [
                    {'plain': "we're "}, {'em': 'three'}, {'plain': ' people'},
                    {'plain': 'who got '}, {'strike': 'tired'}, {'em': 'obsessed'},
                    {'plain': 'with crypto '}, {'em': 'UI'},
                ],
                'lede': 'impuls / studio — a small independent team: trader, designer & engineer.',
                'lede_rest': 'We build products for people who live on the market: terminals, bot infra, token-launch landings.',
                'meta': [
                    {'k': 'founded', 'v': '2024'},
                    {'k': 'headcount', 'v': '3 + 2 freelance'},
                    {'k': 'location', 'v': 'remote · UTC+3'},
                    {'k': 'status', 'v': '● accepting Q3 / 2026', 'accent': True},
                ],
            },
            'nums': [
                {'v': '<em>17</em>', 'k': 'shipped projects'},
                {'v': '2<em>.5</em>', 'k': 'years live'},
                {'v': '<em>$3M</em><sup>+</sup>', 'k': 'turnover on our products'},
                {'v': '12', 'k': 'live in production'},
                {'v': '<em>0</em>', 'k': 'stock 3D blobs used'},
            ],
            'story': {
                'tag': '[ 01 ] / story',
                'h2': 'how we got <em>here</em>.',
                'big': "We started with our own pain. <em>We were trading</em> ourselves — and were constantly annoyed by interfaces where critical data hid behind an accordion.",
                'p': 'In 2024 we built our first internal tool — a bot with an admin to manage strategy. A month later we were asked to do "the same, but for a friend". Three months — first paid project.',
            },
            'final_meta': 'or write directly · <b>hi@impuls.studio</b> · <b>@impuls_studio</b>',
        },
    }
    seo = {
        'ru': {
            'title': 'О студии · impuls / studio',
            'description': 'Команда и философия impuls / studio. Кто мы, как работаем, во что верим.',
            'canonical_path': '/about',
        },
        'en': {
            'title': 'About · impuls / studio',
            'description': 'Team and philosophy of impuls / studio. Who we are, how we work, what we believe in.',
            'canonical_path': '/en/about',
        },
    }
    for lang, payload in base.items():
        payload['lang'] = lang
        payload['seo'] = seo[lang]
        upsert(pb, token, 'page_about', f'lang="{lang}"', payload)


def seed_services(pb, token):
    print('[services]')
    items = {
        'ru': [
            ('product-design', 'Product design', 'terminals · dashboards · flows', 10),
            ('brand', 'Brand & identity', 'naming · guidelines · tokens', 20),
            ('frontend', 'Frontend dev', 'react · next · three.js · realtime ws', 30),
            ('bot-infra', 'Bot infrastructure', 'binance · bybit · fastapi · backtesting', 40),
            ('landing', 'Marketing sites', 'webflow · framer · custom', 50),
        ],
        'en': [
            ('product-design', 'Product design', 'terminals · dashboards · flows', 10),
            ('brand', 'Brand & identity', 'naming · guidelines · tokens', 20),
            ('frontend', 'Frontend dev', 'react · next · three.js · realtime ws', 30),
            ('bot-infra', 'Bot infrastructure', 'binance · bybit · fastapi · backtesting', 40),
            ('landing', 'Marketing sites', 'webflow · framer · custom', 50),
        ],
    }
    for lang, rows in items.items():
        for slug, title, tags, order in rows:
            payload = {
                'lang': lang,
                'slug': slug,
                'title': title,
                'tags': [t.strip() for t in tags.split('·')],
                'order': order,
            }
            upsert(pb, token, 'services', f'slug="{slug}" && lang="{lang}"', payload)


def seed_dispatch(pb, token):
    print('[dispatch]')
    posts = load_fixtures_dispatch()
    for lang in ('ru', 'en'):
        for i, p in enumerate(posts):
            slug = (p.get('title') or '')[:40].lower().replace(' ', '-')
            slug = re.sub(r'[^a-z0-9-]+', '', slug)
            payload = {
                'lang': lang,
                'slug': f"{slug}-{i+1}",
                'title': p.get('title', ''),
                'excerpt': p.get('excerpt', ''),
                'tags': p.get('tags', []),
                'kind': (p.get('tags', [{}])[0] or {}).get('kind', 'default'),
                'read_minutes': 5,
                'published_at': '2026-05-11 10:00:00.000Z',
            }
            upsert(pb, token, 'dispatch',
                   f'slug="{payload["slug"]}" && lang="{lang}"', payload)


CASES_INLINE = [
    {'slug': 'impuls-bot', 'title': 'Impuls-bot v2', 'sub': 'auto-trading platform with backtest engine',
     'tags': ['trading · infra', 'fastapi · react', 'binance · bybit'],
     'meta': ['fastapi', 'react', 'binance'], 'year': "'26", 'status': 'live', 'category': 'trading'},
    {'slug': 'parabolic', 'title': 'Parabolic', 'sub': 'identity for a quant fund — numbers as poetry',
     'tags': ['brand', 'logo · system', 'guidelines'],
     'meta': ['brand'], 'year': "'25", 'status': 'case', 'category': 'brand'},
    {'slug': 'coldstack', 'title': 'Coldstack', 'sub': 'web3 storage protocol launch site',
     'tags': ['landing', 'next · framer', 'shader hero'],
     'meta': ['landing'], 'year': "'25", 'status': 'live', 'category': 'landing'},
    {'slug': 'orderflow', 'title': 'Orderflow', 'sub': 'realtime tape reader for a prop desk',
     'tags': ['trading · ui', 'react · canvas', '200 ws streams'],
     'meta': ['trading'], 'year': "'25", 'status': 'nda', 'category': 'trading'},
    {'slug': 'hedge-ui', 'title': 'Hedge.ui', 'sub': 'hedging terminal — 200 instruments, one screen',
     'tags': ['trading · ui', 'react · websocket', 'naked check'],
     'meta': ['trading'], 'year': "'25", 'status': 'live', 'category': 'trading'},
    {'slug': 'mint-fm', 'title': 'Mint.fm', 'sub': 'curated NFT drop platform — zero fees',
     'tags': ['product · brand', 'full identity', 'marketplace'],
     'meta': ['brand'], 'year': "'25", 'status': 'archive', 'category': 'brand'},
]


def seed_cases(pb, token):
    print('[cases]')
    for lang in ('ru', 'en'):
        for i, c in enumerate(CASES_INLINE):
            payload = dict(c)
            payload['lang'] = lang
            payload['featured'] = i < 6
            payload['order'] = i
            upsert(pb, token, 'cases', f'slug="{c["slug"]}" && lang="{lang}"', payload)


def seed_team(pb, token):
    print('[team]')
    team = {
        'ru': [
            ('Андрей К.', 'trader · founder', '8 лет в трейдинге, до студии — quant-research. Отвечает за продуктовое видение и стратегические части движков.', 'acid', 10),
            ('Мария Л.', 'design lead', 'Бывший арт-директор fintech-стартапа. Десять лет рисует интерфейсы для финансовых продуктов.', 'neutral', 20),
            ('Денис П.', 'engineering', 'Full-stack с уклоном в реалтайм-инфру. Python/FastAPI, React, WebSocket-фанаут.', 'warm', 30),
        ],
        'en': [
            ('Andrey K.', 'trader · founder', '8 years in trading, prior to studio — quant research. Owns product vision and strategy engines.', 'acid', 10),
            ('Maria L.', 'design lead', 'Former art-director at a fintech startup. Ten years drawing interfaces for financial products.', 'neutral', 20),
            ('Denis P.', 'engineering', 'Full-stack with realtime-infra focus. Python/FastAPI, React, WebSocket fanout.', 'warm', 30),
        ],
    }
    for lang, rows in team.items():
        for name, role, bio, accent, order in rows:
            payload = {
                'lang': lang,
                'name': name,
                'role': role,
                'bio': bio,
                'accent': accent,
                'order': order,
                'links': [
                    {'label': 'telegram', 'url': '#'},
                    {'label': 'github', 'url': '#'},
                ],
            }
            upsert(pb, token, 'team', f'name="{name}" && lang="{lang}"', payload)


# ── main ────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pb', required=True)
    ap.add_argument('--email', required=True)
    ap.add_argument('--password', required=True)
    args = ap.parse_args()

    pb = args.pb.rstrip('/')
    token = login(pb, args.email, args.password)

    seed_globals(pb, token)
    seed_page_index(pb, token)
    seed_page_about(pb, token)
    seed_services(pb, token)
    seed_dispatch(pb, token)
    seed_cases(pb, token)
    seed_team(pb, token)

    print('\ndone.')


if __name__ == '__main__':
    main()
