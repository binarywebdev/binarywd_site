#!/usr/bin/env python3
"""
Идемпотентная инициализация PocketBase-схемы для binarywd.com.

Что делает:
  1. Логинится как админ.
  2. Если коллекции `dispatch`, `team`, `globals`, `page_index`, `page_about` нет —
     создаёт по schema_new.
  3. В коллекцию `cases` дописывает поля из cases_extra, не трогая существующие.
  4. На все коллекции (включая cases) ставит правила доступа:
       list/view = `lang != ""`   — публичное чтение
       create/update/delete = ""  — только админ через токен

Запуск:
    python deploy/pb-init.py \
        --pb https://pb.binarywd.com \
        --email hello.chat@binarywd.com \
        --password '<новый-пароль>'
"""

import argparse
import json
import sys
import urllib.request
import urllib.error


# ── helpers ───────────────────────────────────────────────────────────

def http(method, url, body=None, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read().decode() or '{}')
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or '{}')


# ── field shortcuts ───────────────────────────────────────────────────

def text(name, required=False):
    return {'name': name, 'type': 'text', 'required': required, 'options': {}}

def textarea(name, required=False):
    return {'name': name, 'type': 'editor', 'required': required, 'options': {}}

def jsonf(name, required=False):
    return {'name': name, 'type': 'json', 'required': required, 'options': {'maxSize': 2000000}}

def select(name, values, required=False):
    return {'name': name, 'type': 'select', 'required': required,
            'options': {'maxSelect': 1, 'values': values}}

def boolf(name):
    return {'name': name, 'type': 'bool', 'required': False, 'options': {}}

def number(name, required=False):
    return {'name': name, 'type': 'number', 'required': required, 'options': {'noDecimal': False}}

def date(name, required=False):
    return {'name': name, 'type': 'date', 'required': required, 'options': {}}

def file(name, max_select=1):
    return {'name': name, 'type': 'file', 'required': False,
            'options': {'maxSelect': max_select, 'maxSize': 5242880,
                        'mimeTypes': ['image/jpeg', 'image/png', 'image/svg+xml',
                                      'image/webp', 'image/gif']}}


# ── schemas ───────────────────────────────────────────────────────────

PUBLIC_READ = 'lang != ""'

# Доп. поля для существующей коллекции cases
CASES_EXTRA_FIELDS = [
    text('client'),
    file('cover', max_select=1),
    file('gallery', max_select=12),
    jsonf('body_blocks'),
    jsonf('services'),
    jsonf('stack'),
    boolf('featured'),
    date('published_at'),
    number('order'),
]

# Новые коллекции
NEW_COLLECTIONS = [
    {
        'name': 'services',
        'type': 'base',
        'schema': [
            text('slug', required=True),
            text('title', required=True),
            text('subtitle'),
            textarea('body'),
            jsonf('tags'),
            file('icon', max_select=1),
            number('order'),
            select('lang', ['ru', 'en'], required=True),
        ],
        'listRule': PUBLIC_READ,
        'viewRule': PUBLIC_READ,
        'createRule': None,
        'updateRule': None,
        'deleteRule': None,
        'indexes': ['CREATE UNIQUE INDEX idx_services_slug_lang ON services (slug, lang)'],
    },
    {
        # Заявки с контактной формы. Публичный POST (без авторизации),
        # чтение/правка — только админ.
        'name': 'briefs',
        'type': 'base',
        'schema': [
            text('name', required=True),
            text('contact', required=True),
            text('company'),
            jsonf('services'),
            text('budget'),
            textarea('story', required=True),
            text('source'),
            select('lang', ['ru', 'en']),
            select('status', ['new', 'in_review', 'replied', 'archived']),
            text('ip'),
            text('user_agent'),
        ],
        'listRule': None,
        'viewRule': None,
        'createRule': '',
        'updateRule': None,
        'deleteRule': None,
        'indexes': ['CREATE INDEX idx_briefs_created ON briefs (created DESC)'],
    },
    {
        'name': 'dispatch',
        'type': 'base',
        'schema': [
            text('slug', required=True),
            text('title', required=True),
            textarea('excerpt'),
            textarea('body'),
            jsonf('tags'),
            select('kind', ['pin', 'live', 'default']),
            number('read_minutes'),
            date('published_at', required=True),
            select('lang', ['ru', 'en'], required=True),
        ],
        'listRule': PUBLIC_READ,
        'viewRule': PUBLIC_READ,
        'createRule': None,
        'updateRule': None,
        'deleteRule': None,
        'indexes': ['CREATE INDEX idx_dispatch_lang_pub ON dispatch (lang, published_at DESC)'],
    },
    {
        'name': 'team',
        'type': 'base',
        'schema': [
            text('name', required=True),
            text('role'),
            textarea('bio'),
            file('avatar', max_select=1),
            jsonf('links'),
            select('accent', ['neutral', 'acid', 'warm']),
            number('order'),
            select('lang', ['ru', 'en'], required=True),
        ],
        'listRule': PUBLIC_READ,
        'viewRule': PUBLIC_READ,
        'createRule': None,
        'updateRule': None,
        'deleteRule': None,
    },
    {
        'name': 'globals',
        'type': 'base',
        'schema': [
            select('lang', ['ru', 'en'], required=True),
            jsonf('nav_labels'),
            jsonf('manifest_rules'),
            jsonf('ticker_items'),
            jsonf('offices'),
            jsonf('social_links'),
            jsonf('footer_talk'),
            jsonf('legal'),
        ],
        'listRule': PUBLIC_READ,
        'viewRule': PUBLIC_READ,
        'createRule': None,
        'updateRule': None,
        'deleteRule': None,
        'indexes': ['CREATE UNIQUE INDEX idx_globals_lang ON globals (lang)'],
    },
    {
        'name': 'page_index',
        'type': 'base',
        'schema': [
            select('lang', ['ru', 'en'], required=True),
            jsonf('hero'),
            jsonf('services'),
            jsonf('manifest'),
            jsonf('marquee'),
            jsonf('contact_form'),
            jsonf('dispatch'),
            jsonf('work'),
        ],
        'listRule': PUBLIC_READ,
        'viewRule': PUBLIC_READ,
        'createRule': None,
        'updateRule': None,
        'deleteRule': None,
        'indexes': ['CREATE UNIQUE INDEX idx_page_index_lang ON page_index (lang)'],
    },
    {
        'name': 'page_about',
        'type': 'base',
        'schema': [
            select('lang', ['ru', 'en'], required=True),
            jsonf('hero'),
            jsonf('nums'),
            jsonf('story'),
            jsonf('final_meta'),
        ],
        'listRule': PUBLIC_READ,
        'viewRule': PUBLIC_READ,
        'createRule': None,
        'updateRule': None,
        'deleteRule': None,
        'indexes': ['CREATE UNIQUE INDEX idx_page_about_lang ON page_about (lang)'],
    },
]


# ── workflow ──────────────────────────────────────────────────────────

def login(pb, email, password):
    code, data = http('POST', f'{pb}/api/admins/auth-with-password',
                      {'identity': email, 'password': password})
    if code != 200 or 'token' not in data:
        sys.exit(f'auth failed: {code} {data}')
    print(f'[auth] OK')
    return data['token']


def list_collections(pb, token):
    code, data = http('GET', f'{pb}/api/collections?perPage=200', token=token)
    if code != 200:
        sys.exit(f'list collections failed: {code} {data}')
    return {c['name']: c for c in data.get('items', [])}


def create_collection(pb, token, spec):
    code, data = http('POST', f'{pb}/api/collections', spec, token=token)
    if code in (200, 204):
        print(f'[create]  + {spec["name"]}')
    else:
        print(f'[create]  ✗ {spec["name"]}  → {code} {data}')


def patch_collection(pb, token, coll_id, body):
    code, data = http('PATCH', f'{pb}/api/collections/{coll_id}', body, token=token)
    if code == 200:
        print(f'[patch]   OK {coll_id}')
    else:
        print(f'[patch]   ✗ {coll_id}  → {code} {data}')


def ensure_cases_extra_fields(pb, token, existing):
    ensure_extra_fields(pb, token, existing, 'cases', CASES_EXTRA_FIELDS)


def ensure_extra_fields(pb, token, existing, name, extra_fields):
    coll = existing.get(name)
    if not coll:
        print(f'[{name}]   X collection not found, skip')
        return
    have = {f['name'] for f in coll.get('schema', [])}
    missing = [f for f in extra_fields if f['name'] not in have]
    if not missing:
        print(f'[{name}]   OK all extra fields already present')
        return
    new_schema = coll['schema'] + missing
    patch_collection(pb, token, coll['id'], {'schema': new_schema})
    print(f'[{name}]   + appended: {[f["name"] for f in missing]}')


# Доп. поля для уже существующих синглетонов — заведутся идемпотентно
PAGE_INDEX_EXTRA = [jsonf('manifest'), jsonf('dispatch'), jsonf('work'), jsonf('seo')]
PAGE_ABOUT_EXTRA = [jsonf('seo')]
GLOBALS_EXTRA = [jsonf('seo_defaults'), jsonf('footer_misc'), text('contact_email'),
                 text('contact_telegram'), text('response_sla'), text('version'),
                 jsonf('brand')]
CASES_SEO_EXTRA = [jsonf('seo')]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pb', required=True, help='PocketBase base URL')
    ap.add_argument('--email', required=True)
    ap.add_argument('--password', required=True)
    args = ap.parse_args()

    pb = args.pb.rstrip('/')
    token = login(pb, args.email, args.password)
    existing = list_collections(pb, token)
    print(f'[scan]    found {len(existing)} collections: {list(existing.keys())}')

    # 1) Create missing new collections
    for spec in NEW_COLLECTIONS:
        if spec['name'] in existing:
            print(f'[skip]    = {spec["name"]} already exists')
            continue
        create_collection(pb, token, spec)

    # 2) Extend existing collections with new fields
    existing = list_collections(pb, token)  # refresh
    ensure_cases_extra_fields(pb, token, existing)
    ensure_extra_fields(pb, token, existing, 'page_index', PAGE_INDEX_EXTRA)
    ensure_extra_fields(pb, token, existing, 'page_about', PAGE_ABOUT_EXTRA)
    ensure_extra_fields(pb, token, existing, 'globals',    GLOBALS_EXTRA)
    ensure_extra_fields(pb, token, existing, 'cases',      CASES_SEO_EXTRA)

    print('\ndone.')


if __name__ == '__main__':
    main()
