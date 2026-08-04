#!/usr/bin/env python3
"""
Roovel Studio — site build.

index.html tek kaynaktır. Bu betik ondan:
  /games/index.html, /studio/index.html, /press/index.html,
  /contact/index.html, /privacy/index.html
  404.html, sitemap.xml, robots.txt
üretir.

index.html'i her düzenledikten sonra çalıştır:   python3 build.py
"""
import os, re, shutil, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(ROOT, "index.html")
BASE = "https://roovelstudio.com"

# SPA rotasi olmayan, elle yonetilen bagimsiz sayfalar
EXTRA_URLS = ["/join"]

# rota -> (yol, <title>, meta description, og görseli)
PAGES = {
    "home": ("/",        "Roovel Studio — Indie Games from Denizli",
                "Roovel Studio is an indie game studio in Denizli, Türkiye, crafting systems-driven games with sharp mechanics and a lot of heart.", "og.jpg"),
    "games": ("/games",   "Games — Roovel Studio",
                "Everything Roovel has shipped and everything loading next: Deal Flipper, Everybody Loves a Good Hole, UNTRASH and more.", "og-games.jpg"),
    "studio": ("/studio",  "Studio — Roovel Studio",
                "Four people in Denizli, Türkiye, building systems-driven games. Meet the team behind Roovel.", "og.jpg"),
    "press": ("/press",   "Press Kit — Roovel Studio",
                "Facts, assets, review keys and creator policy for Roovel Studio and our games.", "og.jpg"),
    "contact": ("/contact", "Contact — Roovel Studio",
                "Press, publishing, playtests or just a hello — get in touch with Roovel Studio.", "og.jpg"),
    "privacy": ("/privacy", "Privacy Policy — Roovel Studio",
                "How Roovel Studio handles the small amount of data this website collects.", "og.jpg"),
}

def sub_once(html, pattern, repl, label):
    out, n = re.subn(pattern, lambda m: repl, html, count=1)
    if n != 1:
        raise SystemExit(f"build hatası: {label} bulunamadı ({n} eşleşme)")
    return out

def make_page(html, route):
    path, title, desc, ogimg = PAGES[route]
    ogurl = f"{BASE}/assets/{ogimg}"
    url = BASE + ("" if path == "/" else path)

    html = sub_once(html, r"<title>.*?</title>", f"<title>{title}</title>", "title")
    html = sub_once(html, r'<meta name="description" content="[^"]*">',
                    f'<meta name="description" content="{desc}">', "meta description")
    html = sub_once(html, r'<link rel="canonical" href="[^"]*">',
                    f'<link rel="canonical" href="{url}">', "canonical")
    html = sub_once(html, r'<meta property="og:url" content="[^"]*">',
                    f'<meta property="og:url" content="{url}">', "og:url")
    html = sub_once(html, r'<meta property="og:title" content="[^"]*">',
                    f'<meta property="og:title" content="{title}">', "og:title")
    html = sub_once(html, r'<meta property="og:description" content="[^"]*">',
                    f'<meta property="og:description" content="{desc}">', "og:description")
    html = sub_once(html, r'<meta name="twitter:title" content="[^"]*">',
                    f'<meta name="twitter:title" content="{title}">', "twitter:title")
    html = sub_once(html, r'<meta name="twitter:description" content="[^"]*">',
                    f'<meta name="twitter:description" content="{desc}">', "twitter:description")
    html = sub_once(html, r'<meta property="og:image" content="[^"]*">',
                    f'<meta property="og:image" content="{ogurl}">', "og:image")
    html = sub_once(html, r'<meta name="twitter:image" content="[^"]*">',
                    f'<meta name="twitter:image" content="{ogurl}">', "twitter:image")

    # sunucudan gelen sayfa doğru bölümle açılsın (JS yüklenmeden önce de doğru)
    if route != "home":
        html = html.replace('<div class="page active" id="page-home">',
                            '<div class="page" id="page-home">')
        html = html.replace(f'<div class="page" id="page-{route}">',
                            f'<div class="page active" id="page-{route}">')
        html = html.replace(f'<a href="{path}" data-route="{route}" class="active">',
                            f'<a href="{path}" data-route="{route}" class="active">')
    return html

def main():
    src = open(SRC, encoding="utf-8").read()
    built = []

    for route in PAGES:
        if route == "home":
            continue
        path = PAGES[route][0].strip("/")
        d = os.path.join(ROOT, path)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(make_page(src, route))
        built.append(f"{path}/index.html")

    # 404: bilinmeyen yollar ana sayfayı gösterir
    open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8").write(make_page(src, "home"))
    built.append("404.html")

    today = datetime.date.today().isoformat()
    entries = [(p, '1.0' if p == '/' else ('0.5' if p == '/privacy' else '0.8'))
               for p, _, _, _ in PAGES.values()]
    # SPA disinda duran bagimsiz sayfalar
    entries += [(u, '0.7') for u in EXTRA_URLS]
    urls = "\n".join(
        f"  <url><loc>{BASE}{'' if p == '/' else p}</loc>"
        f"<lastmod>{today}</lastmod>"
        f"<priority>{pr}</priority></url>"
        for p, pr in entries
    )
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n</urlset>\n")
    built.append("sitemap.xml")

    open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8").write(
        f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")
    built.append("robots.txt")

    # GitHub Pages'in Jekyll işlemesini kapat
    open(os.path.join(ROOT, ".nojekyll"), "w").close()
    built.append(".nojekyll")

    print("üretildi:")
    for b in built:
        print("  " + b)

if __name__ == "__main__":
    main()
