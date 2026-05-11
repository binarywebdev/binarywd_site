# binarywd.com — серверная настройка

Раскладка: **root = студия (статика Astro)**, **pb = pocketbase**, **www = redirect на root**.

⚠️ На сервере уже крутятся **другие сайты** — каждый шаг проектирует так, чтобы их **не задеть**. Конфиги — самодостаточные vhost-ы, ничего глобального не правим.

Все шаги выполняешь **сам по SSH** под `sudo`.

---

## 0. Pre-flight — что уже есть на сервере

Прежде чем что-то трогать — снимаем фотографию текущего состояния.

```bash
# Какие vhost-ы активны сейчас? (запомни, скопируй на всякий)
sudo ls -la /etc/nginx/sites-enabled/

# Какие server_name заняты — особенно ищи binarywd.com и default_server
sudo grep -rn "server_name\|default_server" /etc/nginx/sites-enabled/ /etc/nginx/conf.d/

# Какие порты слушаются (нам важен 8090 для PocketBase)
sudo ss -tlnp | grep -E '^|:8090|:80\s|:443\s'

# Backup всего nginx (на случай если что-то пойдёт не так — откатишься)
sudo cp -a /etc/nginx /root/nginx-backup-$(date +%Y%m%d-%H%M%S)
```

Запиши себе:
- **Список доменов-соседей** (что в `sites-enabled/`) — мы их **не трогаем**.
- **Порт uvicorn торгового бота** (`8000`? `8001`? — увидишь в `ss -tlnp`).
- **Где сейчас прописан `binarywd.com`** в существующих конфигах — нужно убрать только из server_name, не удаляя сам vhost (см. п. 2).

---

## 0.1. Проверь что порты PB не заняты

```bash
sudo ss -tlnp | grep :8090
# должно вернуть пусто. Если занято — найди другой свободный порт
# и поменяй его в pb.binarywd.com.conf (upstream pocketbase) и в pocketbase.service (--http=127.0.0.1:XXXX)
```

---

## 0.2. DNS пропогнался

```bash
dig +short binarywd.com pb.binarywd.com www.binarywd.com
# Все три → 213.199.59.61
```

---

## 1. Папки и owner — только для нашего сайта

```bash
sudo mkdir -p /var/www/binarywd.com/dist
sudo mkdir -p /var/www/_letsencrypt   # общая папка для ACME (если ещё нет)

# Если /var/www/_letsencrypt уже существует (есть соседние сайты с certbot) — не трогаем permissions, проверяем что www-data может туда писать.
sudo chown -R $USER:www-data /var/www/binarywd.com
sudo chmod -R 755 /var/www/binarywd.com

# временная заглушка, чтобы certbot увидел контент
echo "<h1>binarywd.com — coming soon</h1>" | sudo tee /var/www/binarywd.com/dist/index.html
```

---

## 2. Снять `binarywd.com` со старого vhost-а (если есть)

Если в p.0 ты увидел что `binarywd.com` уже прописан в каком-то существующем vhost — нужно его оттуда убрать, чтобы наш новый конфиг подхватил домен. Открой файл:

```bash
sudo nano /etc/nginx/sites-available/<имя-старого-конфига>.conf
```

В строке `server_name` **убери только `binarywd.com`** (если он там есть), оставив всё остальное. Например:

**Было:**
```nginx
server_name binarywd.com 213.199.59.61 _;
```
**Стало:**
```nginx
server_name 213.199.59.61 _;
```

Если этого vhost-а **нет** и `binarywd.com` нигде не упомянут — пропускай этот шаг.

Сохрани, **пока не релоудь** (релоудим разом в п. 3).

---

## 3. Загрузить конфиги и валидировать

С локалки:
```bash
scp deploy/nginx/binarywd.com.conf     user@213.199.59.61:/tmp/
scp deploy/nginx/pb.binarywd.com.conf  user@213.199.59.61:/tmp/
scp deploy/systemd/pocketbase.service  user@213.199.59.61:/tmp/
```

На сервере:
```bash
sudo mv /tmp/binarywd.com.conf      /etc/nginx/sites-available/
sudo mv /tmp/pb.binarywd.com.conf   /etc/nginx/sites-available/

# симлинки
sudo ln -s /etc/nginx/sites-available/binarywd.com.conf     /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/pb.binarywd.com.conf  /etc/nginx/sites-enabled/

# ТЕСТ — ничего не релоудим, пока не валидно
sudo nginx -t
```

**Если nginx -t падает на conflicting server_name** — значит `binarywd.com` остался в чужом vhost. Вернись к п. 2.
**Если ОК (`syntax is ok` + `test is successful`)**:
```bash
sudo systemctl reload nginx
```

Reload — мягкий, активные соединения соседних сайтов не порвутся.

---

## 4. SSL — Let's Encrypt (на 3 хоста разом, ничего соседнего не трогая)

```bash
which certbot || sudo apt install -y certbot python3-certbot-nginx

sudo certbot --nginx \
  -d binarywd.com \
  -d www.binarywd.com \
  -d pb.binarywd.com \
  --agree-tos -m your@email.here --redirect --no-eff-email
```

Certbot:
- Делает HTTP-01 challenge через наши `:80`-блоки → берёт сертификат.
- Сам **дописывает 443-блоки** в наших конфигах, копируя содержимое из `:80`-блока (gzip, headers, кеш всё переедет).
- Сам **меняет :80-блоки на 301 → https**.
- Других vhost-ов **не трогает** — он работает только с теми server_name, которые ты передал через `-d`.

Проверка авто-обновления:
```bash
sudo certbot renew --dry-run
sudo systemctl list-timers | grep certbot
```

---

## 5. PocketBase

```bash
sudo useradd -r -s /usr/sbin/nologin -d /opt/pocketbase pocketbase
sudo mkdir -p /opt/pocketbase
sudo chown pocketbase:pocketbase /opt/pocketbase

cd /tmp
PB_VERSION="0.22.21"
wget "https://github.com/pocketbase/pocketbase/releases/download/v${PB_VERSION}/pocketbase_${PB_VERSION}_linux_amd64.zip"
unzip "pocketbase_${PB_VERSION}_linux_amd64.zip"
sudo mv pocketbase /opt/pocketbase/pocketbase
sudo chmod +x /opt/pocketbase/pocketbase
sudo chown pocketbase:pocketbase /opt/pocketbase/pocketbase

sudo mv /tmp/pocketbase.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now pocketbase

sudo systemctl status pocketbase --no-pager
sudo ss -tlnp | grep 8090
```

Открой **https://pb.binarywd.com/_/** — там создашь первого админа.

---

## 6. Деплой Astro билда

С локалки:
```bash
cd /c/xampp/htdocs/binarywd.local
npm run build

rsync -avz --delete dist/ user@213.199.59.61:/var/www/binarywd.com/dist/
```

`--delete` чистит файлы которые исчезли в новом билде — но **только внутри** `/var/www/binarywd.com/dist/`. Соседние сайты в `/var/www/<other>/` не трогаются.

Открой **https://binarywd.com/**.

---

## 7. Проверки — каждый хост и что соседи живы

```bash
# наши новые хосты
curl -sI https://binarywd.com/      | head -3   # 200 + content-type text/html
curl -sI https://www.binarywd.com/  | head -3   # 301 → binarywd.com
curl -sI https://pb.binarywd.com/_/ | head -3   # 200 от PB-админки

# соседи живы? (заполни своими доменами)
curl -sI https://example1.com/ | head -3
curl -sI https://example2.com/ | head -3
```

---

## 8. Откат — если что-то пошло не так

```bash
# восстанови nginx из бекапа
sudo rm -rf /etc/nginx
sudo mv /root/nginx-backup-<timestamp> /etc/nginx
sudo nginx -t && sudo systemctl reload nginx

# выруби PB
sudo systemctl disable --now pocketbase
```

---

## 9. Cloudflare proxy (опционально, позже)

После того как всё стабильно работает на DNS-only:

- В Cloudflare DNS — переключи **серые облачка на оранжевые** для `binarywd.com`, `www`, `pb`.
- SSL/TLS mode → **Full (strict)** (у нас Let's Encrypt с реальными сертификатами).
- Auto Minify → выключи (Astro минифицирован, дублирование ломает inline-JS).
- Brotli / HTTP/3 → on.

---

## 10. Дальше — контент

- Создать в PB-админке коллекции `cases`, `dispatch`, `team`, `globals` (схемы в `README.md` корня).
- В `src/lib/pocketbase.ts` раскомментировать `getCases`/`getDispatch`, заменить fixtures на реальные запросы.
- Авто-ребилд при правке контента: webhook PB → CI → `npm run build` → rsync.
