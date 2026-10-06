#!/usr/bin/env python3
"""
Вносит базовое SEO в index.html и генерирует отдельные файлы страниц
(about.html, jobs.html, promotions.html, contacts.html), robots.txt и sitemap.xml.

Запуск:  python3 build_pages.py <исходный index.html> <папка вывода>
Источник правды по title/description/URL — словарь PAGES ниже.
"""
import html, json, re, sys, os

SRC = sys.argv[1]
OUT = sys.argv[2]
SITE = "https://pizzaudona.ru/"          # <-- замените на реальный домен
OG_IMAGE = "https://images.unsplash.com/photo-1594007654729-407eedc4be65?auto=format&fit=crop&w=1200&h=630&q=80"
OG_IMAGE_ALT = "Пицца с грушей и горгонзолой — Пицца у Дона"
LASTMOD = "2026-10-06"

PAGES = {
    "viewMenu": dict(
        file="index.html", url=SITE, ogType="website", priority="1.0",
        title="Пицца у Дона — доставка пиццы за 30 минут в Москве",
        description="Горячая пицца из дровяной печи: Маргарита, Пепперони, Четыре сыра. Доставка за 30 минут по Москве. Скидка 20% на первый заказ — выбирайте и заказывайте!",
    ),
    "viewAbout": dict(
        file="about.html", url=SITE + "about.html", ogType="article", priority="0.7",
        title="О нас — семейная пиццерия «Пицца у Дона» в Москве",
        description="Как мы готовим пиццу: дровяная печь, тесто на опаре 72 часа, свежие ингредиенты и семейный рецепт. Загляните в гости или закажите доставку на дом!",
    ),
    "viewJobs": dict(
        file="jobs.html", url=SITE + "jobs.html", ogType="article", priority="0.6",
        title="Работа в «Пицце у Дона» — вакансии повара и курьера",
        description="Ищем поваров-пиццайоло, курьеров, кассиров и менеджеров смены в Москве. Присоединяйтесь к команде семейной пиццерии — откликнитесь на вакансию онлайн!",
    ),
    "viewPromotions": dict(
        file="promotions.html", url=SITE + "promotions.html", ogType="article", priority="0.8",
        title="Акции и скидки — 2-я пицца в подарок | Пицца у Дона",
        description="2-я пицца в подарок от 1000 ₽, скидка 20% на первый заказ, бесплатная доставка и −15% в день рождения. Выберите акцию и закажите пиццу сегодня!",
    ),
    "viewContacts": dict(
        file="contacts.html", url=SITE + "contacts.html", ogType="article", priority="0.7",
        title="Контакты — Пицца у Дона, Москва, ул. Тверская, 12",
        description="Пиццерия на ул. Тверская, 12 работает ежедневно с 10:00 до 23:00. Звоните +7 (000) 000-00-00 или оставьте сообщение на сайте — ответим быстро!",
    ),
}

for k, p in PAGES.items():
    assert len(p["title"]) <= 60, (k, len(p["title"]), p["title"])
    assert len(p["description"]) <= 160, (k, len(p["description"]))

JSON_LD = {
    "@context": "https://schema.org",
    "@type": "Restaurant",
    "name": "Пицца у Дона",
    "description": "Семейная пиццерия: пицца из дровяной печи с доставкой за 30 минут.",
    "url": SITE,
    "image": [OG_IMAGE],
    "telephone": "+7-000-000-00-00",
    "servesCuisine": ["Пицца", "Итальянская"],
    "priceRange": "₽₽",
    "currenciesAccepted": "RUB",
    "hasMenu": SITE + "#menu",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "ул. Тверская, 12",
        "addressLocality": "Москва",
        "addressCountry": "RU",
    },
    "openingHoursSpecification": [{
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "opens": "10:00",
        "closes": "23:00",
    }],
}


def esc(s):
    return html.escape(s, quote=True)


def seo_block(view_id, with_jsonld):
    p = PAGES[view_id]
    lines = [
        "<!-- SEO:START -->",
        f"<title>{esc(p['title'])}</title>",
        f'<meta name="description" content="{esc(p["description"])}">',
        '<meta name="robots" content="index, follow">',
        f'<link rel="canonical" href="{p["url"]}">',
        '<meta name="theme-color" content="#E8590C">',
        "",
        "<!-- Open Graph -->",
        '<meta property="og:site_name" content="Пицца у Дона">',
        '<meta property="og:locale" content="ru_RU">',
        f'<meta property="og:type" content="{p["ogType"]}">',
        f'<meta property="og:title" content="{esc(p["title"])}">',
        f'<meta property="og:description" content="{esc(p["description"])}">',
        f'<meta property="og:url" content="{p["url"]}">',
        f'<meta property="og:image" content="{OG_IMAGE}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{esc(OG_IMAGE_ALT)}">',
        "",
        "<!-- Twitter / мессенджеры -->",
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{esc(p["title"])}">',
        f'<meta name="twitter:description" content="{esc(p["description"])}">',
        f'<meta name="twitter:image" content="{OG_IMAGE}">',
    ]
    if with_jsonld:
        lines += [
            "",
            "<!-- Структурированные данные (JSON-LD) -->",
            '<script type="application/ld+json">',
            json.dumps(JSON_LD, ensure_ascii=False, indent=2),
            "</script>",
        ]
    lines.append("<!-- SEO:END -->")
    return "\n".join(lines)


def sub1(src, old, new, count=1):
    n = src.count(old)
    assert n == count, f"ожидалось {count} вхождений, найдено {n}: {old[:70]!r}"
    return src.replace(old, new)


src = open(SRC, encoding="utf-8").read()

# ---------- 1. HEAD: title + meta + OG + JSON-LD ----------
src = sub1(src, "<title>Пицца у Дона — горячая пицца за 30 минут</title>", seo_block("viewMenu", True))

# ---------- 2. Семантика ----------
# названия пицц — h2 (только карточки пицц; комбо/закуски остаются h3)
src = sub1(src, "<h3>${pizza.name}</h3>", "<h2>${pizza.name}</h2>")
src = sub1(src, "  .pizza-card h3{", "  .pizza-card h2,\n  .pizza-card h3{")

# кнопки карточек: понятный текст + aria-label
src = sub1(
    src,
    '<button type="button" class="btn btn-primary btn-block" data-open="${pizza.id}">${priceLabel(pizza)}</button>',
    '<button type="button" class="btn btn-primary btn-block" data-open="${pizza.id}" aria-label="Выбрать пиццу «${pizza.name}», ${priceLabel(pizza)}">Выбрать · ${priceLabel(pizza)}</button>',
)
src = sub1(
    src,
    '<button type="button" class="btn btn-primary btn-block" data-open="${item.id}">${priceLabel(item)}</button>',
    '<button type="button" class="btn btn-primary btn-block" data-open="${item.id}" aria-label="Выбрать: ${item.name}, ${priceLabel(item)}">Выбрать · ${priceLabel(item)}</button>',
)

# hero-кнопка
src = sub1(src, '<a href="#menu" class="btn btn-primary">Заказать 🍕</a>',
           '<a href="#menu" class="btn btn-primary">Заказать пиццу 🍕</a>')

# акции: «Заказать» -> «Заказать по акции» (+ контекст в aria-label)
promo_titles = ["2-я пицца в подарок", "Скидка 20% на первый заказ",
                "Бесплатная доставка от 1000 ₽", "День рождения — скидка 15%"]
parts = src.split('<button type="button" class="btn btn-primary" data-order-offer>Заказать</button>')
assert len(parts) == 5
src = parts[0]
for t, rest in zip(promo_titles, parts[1:]):
    src += (f'<button type="button" class="btn btn-primary" data-order-offer '
            f'aria-label="Заказать по акции: {t}">Заказать по акции</button>') + rest

# вакансии: уточняем действие в aria-label
for pos in ["Повар-пиццайоло", "Курьер", "Кассир", "Менеджер смены"]:
    src = sub1(src,
               f'<button type="button" class="btn btn-primary" data-apply="{pos}">Откликнуться</button>',
               f'<button type="button" class="btn btn-primary" data-apply="{pos}" aria-label="Откликнуться на вакансию: {pos}">Откликнуться</button>')

# Telegram-кнопка
src = sub1(src, '<a class="btn btn-primary" href="#">Подписаться</a>',
           '<a class="btn btn-primary" href="#">Подписаться в Telegram</a>')

# навигация: реальные ссылки вместо href="#" (их видят поисковики)
nav_map = {"viewMenu": "index.html", "viewAbout": "about.html", "viewJobs": "jobs.html",
           "viewPromotions": "promotions.html", "viewContacts": "contacts.html"}
src = sub1(src, '<li><a href="#top" data-nav="viewMenu" class="active">Меню</a></li>',
           '<li><a href="index.html" data-nav="viewMenu" class="active">Меню</a></li>')
src = sub1(src, '<li><a href="#top" data-nav="viewMenu">Меню</a></li>',
           '<li><a href="index.html" data-nav="viewMenu">Меню</a></li>')
for vid, f in nav_map.items():
    if vid == "viewMenu":
        continue
    src = sub1(src, f'<a href="#" data-nav="{vid}">', f'<a href="{f}" data-nav="{vid}">', count=2)
src = sub1(src, '<a class="logo" href="#top" id="logoLink">',
           '<a class="logo" href="index.html" id="logoLink" aria-label="Пицца у Дона — на главную">')
src = sub1(src, '<nav class="nav-inline">', '<nav class="nav-inline" aria-label="Основная навигация">')

# ---------- 3. JS: мета-теги и URL меняются при переключении «страниц» ----------
pages_js = {vid: dict(file=p["file"], url=p["url"], title=p["title"],
                      description=p["description"], ogType=p["ogType"])
            for vid, p in PAGES.items()}

routing_js = """  /* ---------------------------------------------
     SEO: у каждой «страницы» свой URL, title, description, canonical и Open Graph.
     Те же значения прописаны статически в <head> каждого HTML-файла (для роботов
     и превью в мессенджерах); здесь они синхронизируются при навигации без перезагрузки.
  --------------------------------------------- */
  const PAGES = %s;

  function setHead(selector, attr, value){
    const el = document.querySelector(selector);
    if (el) el.setAttribute(attr, value);
  }
  function currentFile(){
    return location.pathname.split('/').pop() || 'index.html';
  }
  function viewByLocation(){
    const f = currentFile();
    return Object.keys(PAGES).find(id => PAGES[id].file === f) || 'viewMenu';
  }
  function applyPageMeta(id, push){
    const p = PAGES[id];
    if (!p){
      // Оформление заказа — не отдельная индексируемая страница: меняем только заголовок
      if (id === 'viewOrder') document.title = 'Оформление заказа — Пицца у Дона';
      return;
    }
    document.title = p.title;
    setHead('meta[name="description"]', 'content', p.description);
    setHead('link[rel="canonical"]', 'href', p.url);
    setHead('meta[property="og:title"]', 'content', p.title);
    setHead('meta[property="og:description"]', 'content', p.description);
    setHead('meta[property="og:url"]', 'content', p.url);
    setHead('meta[property="og:type"]', 'content', p.ogType);
    setHead('meta[name="twitter:title"]', 'content', p.title);
    setHead('meta[name="twitter:description"]', 'content', p.description);
    if (push && currentFile() !== p.file){
      try { history.pushState({ view:id }, '', p.file); } catch (err) { /* file:// — адрес не меняем */ }
    }
  }

  function showView(id, push = true){""" % json.dumps(pages_js, ensure_ascii=False, indent=4).replace("\n", "\n  ")

src = sub1(src, "  function showView(id){", routing_js)
src = sub1(src, "    closeMobileNav();\n    // Слайдер в hero живёт",
           "    closeMobileNav();\n    applyPageMeta(id, push);\n    // Слайдер в hero живёт")
src = sub1(src, "  function showMenu(){ showView('viewMenu'); }",
           "  function showMenu(){ showView('viewMenu'); }\n\n"
           "  // Кнопки «назад/вперёд» в браузере\n"
           "  window.addEventListener('popstate', () => showView(viewByLocation(), false));")

# клик по пунктам меню: не перехватываем Ctrl/Cmd/средний клик (открытие в новой вкладке)
src = sub1(src,
           "    a.addEventListener('click', e => {\n      e.preventDefault();\n      showView(a.dataset.nav);",
           "    a.addEventListener('click', e => {\n      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button === 1) return;\n      e.preventDefault();\n      showView(a.dataset.nav);")
src = sub1(src,
           "  document.getElementById('logoLink').addEventListener('click', e => {\n    e.preventDefault();",
           "  document.getElementById('logoLink').addEventListener('click', e => {\n    if (e.metaKey || e.ctrlKey || e.shiftKey || e.button === 1) return;\n    e.preventDefault();")

# ---------- 4. Запись файлов ----------
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(src)

block_re = re.compile(r"<!-- SEO:START -->.*?<!-- SEO:END -->", re.S)
for vid, p in PAGES.items():
    if vid == "viewMenu":
        continue
    page = block_re.sub(lambda m: seo_block(vid, False), src, count=1)
    # активный экран и пункт меню — статически, чтобы страница открывалась сразу нужной
    page = sub1(page, '<div class="view active" id="viewMenu">', '<div class="view" id="viewMenu">')
    page = sub1(page, f'<div class="view" id="{vid}">', f'<div class="view active" id="{vid}">')
    page = sub1(page, '<li><a href="index.html" data-nav="viewMenu" class="active">Меню</a></li>',
                '<li><a href="index.html" data-nav="viewMenu">Меню</a></li>')
    page = sub1(page, f'<li><a href="{p["file"]}" data-nav="{vid}">',
                f'<li><a href="{p["file"]}" data-nav="{vid}" class="active">', count=2)
    open(os.path.join(OUT, p["file"]), "w", encoding="utf-8").write(page)

open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8").write(
    "User-agent: *\nAllow: /\n\nSitemap: " + SITE + "sitemap.xml\n")

urls = "\n".join(
    f"  <url>\n    <loc>{p['url']}</loc>\n    <lastmod>{LASTMOD}</lastmod>\n"
    f"    <changefreq>{'weekly' if vid in ('viewMenu', 'viewPromotions') else 'monthly'}</changefreq>\n"
    f"    <priority>{p['priority']}</priority>\n  </url>"
    for vid, p in PAGES.items())
open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "\n</urlset>\n")

for vid, p in PAGES.items():
    print(f"{p['file']:<16} title={len(p['title']):>2}  desc={len(p['description']):>3}")
