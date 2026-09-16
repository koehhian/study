#!/usr/bin/env python3
"""Generate discovery metadata from the site's linked, public HTML pages.

Run after editing article titles/descriptions or adding homepage/series links.
Standard library only; no server-side runtime or build service required.
"""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, unquote
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://study.samkoeh.com/'
START, END = '<!-- discovery:start -->', '<!-- discovery:end -->'


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.title = ''
        self.description = ''
        self.links = []
        self.sections = []
        self.ids = set()
        self.in_title = False
        self.heading = None
        self.section_id = None
        self.in_head = False
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'head':
            self.in_head = True
        if tag == 'title' and self.in_head:
            self.in_title = True
        if tag == 'meta' and a.get('name') == 'description':
            self.description = a.get('content', '')
        if 'id' in a:
            self.ids.add(a['id'])
        if tag == 'section':
            self.section_id = a.get('id')
        if tag == 'a' and a.get('href'):
            self.links.append(a['href'])
        if tag == 'h2':
            self.heading = {'title': '', 'fragment': a.get('id') or self.section_id}

    def handle_endtag(self, tag):
        if tag == 'head':
            self.in_head = False
        if tag == 'title':
            self.in_title = False
        if tag == 'h2' and self.heading:
            self.heading['title'] = self.heading['title'].strip()
            self.sections.append(self.heading)
            self.heading = None
        if tag == 'section':
            self.section_id = None

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.heading is not None:
            self.heading['title'] += data


def file_for(url):
    parts = urlsplit(url)
    if parts.netloc != urlsplit(BASE).netloc:
        return None
    path = ROOT / unquote(parts.path).lstrip('/')
    if path.is_dir():
        path /= 'index.html'
    if path.suffix != '.html' or not path.is_file() or not path.resolve().is_relative_to(ROOT):
        return None
    return path


def canonical(path):
    relative = path.relative_to(ROOT).as_posix()
    if relative.endswith('index.html'):
        relative = relative[:-10]
    return BASE + relative


def main():
    pages = {}
    pending = [ROOT / 'index.html']
    while pending:
        path = pending.pop(0)
        if path in pages:
            continue
        source = path.read_text()
        page = Page(source)
        assert page.title and page.description, f'Missing title/description: {path}'
        pages[path] = (source, page)
        for href in page.links:
            target = file_for(urljoin(canonical(path), href))
            if target is not None and target not in pages:
                pending.append(target)

    records = []
    for path, (source, page) in pages.items():
        url = canonical(path)
        collection = path in (ROOT / 'index.html', ROOT / 'nt-politics/index.html')
        series_article = path.parent.parent == ROOT / 'nt-politics'
        kind = 'CollectionPage' if collection else 'Article'
        schema = {
            '@context': 'https://schema.org', '@type': kind,
            '@id': url + '#document', 'url': url, 'name': page.title,
            'description': page.description, 'inLanguage': 'zh-Hant-TW',
            'isPartOf': {'@id': BASE + '#website'},
        }
        if collection:
            linked = list(dict.fromkeys(canonical(t) for h in page.links
                          if (t := file_for(urljoin(url, h))) in pages and canonical(t) != url))
            if path != ROOT / 'index.html':
                linked = [u for u in linked if u.startswith(url)]
            schema['mainEntity'] = {'@type': 'ItemList', 'itemListElement': [
                {'@type': 'ListItem', 'position': i, 'url': u}
                for i, u in enumerate(linked, 1)]}
        else:
            schema.update(headline=page.title,
                          author={'@type': 'Person', 'name': 'Sam Koeh', 'url': BASE + '#about'},
                          mainEntityOfPage=url)
            if series_article:
                schema['isPartOf'] = {'@type': 'CreativeWorkSeries', 'name': '新約政治史', 'url': BASE + 'nt-politics/'}
            credit = '<p class="study-credit" style="margin:24px; font-size:14px; line-height:1.8">研究整理：<a href="' + BASE + '#about">Sam Koeh</a> · <a href="' + BASE + '">返回 Study</a></p>'
            if 'class="study-credit"' not in source:
                source = source.replace('</body>', credit + '\n</body>', 1)
        graph = [schema]
        if path == ROOT / 'index.html':
            graph.append({'@context': 'https://schema.org', '@type': 'WebSite', '@id': BASE + '#website',
                          'url': BASE, 'name': 'Sam Koeh Study', 'inLanguage': 'zh-Hant-TW'})
        e = lambda value: escape(value, quote=True)
        tags = [START,
                f'<link rel="canonical" href="{e(url)}">',
                '<link rel="alternate" type="application/json" href="/catalog.json" title="研究目錄（JSON）">',
                '<meta property="og:site_name" content="Sam Koeh Study">',
                '<meta property="og:locale" content="zh_TW">',
                f'<meta property="og:type" content="{"website" if collection else "article"}">',
                f'<meta property="og:title" content="{e(page.title)}">',
                f'<meta property="og:description" content="{e(page.description)}">',
                f'<meta property="og:url" content="{e(url)}">',
                '<meta name="twitter:card" content="summary">',
                '<script type="application/ld+json">' + json.dumps(graph, ensure_ascii=False).replace('<', '\\u003c') + '</script>', END]
        source = re.sub(re.escape(START) + r'.*?' + re.escape(END) + r'\s*', '', source, flags=re.S)
        source = source.replace('</head>', '\n'.join(tags) + '\n</head>', 1)
        path.write_text(source)
        record = {'url': url, 'title': page.title, 'description': page.description, 'type': kind,
                  'language': 'zh-Hant-TW', 'sections': [
                      {'title': h['title'], 'url': url + '#' + h['fragment']}
                      for h in page.sections if h['fragment'] in page.ids]}
        if series_article:
            record.update(series='新約政治史', position=int(path.parent.name))
        records.append(record)

    records.sort(key=lambda r: r['url'])
    (ROOT / 'catalog.json').write_text(json.dumps({'site': BASE, 'pages': records}, ensure_ascii=False, indent=2) + '\n')
    ns = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('', ns)
    sitemap = ET.Element('{' + ns + '}urlset')
    for record in records:
        item = ET.SubElement(sitemap, '{' + ns + '}url')
        ET.SubElement(item, '{' + ns + '}loc').text = record['url']
    ET.ElementTree(sitemap).write(ROOT / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    (ROOT / 'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: ' + BASE + 'sitemap.xml\n')
    lines = ['# Sam Koeh Study', '', '> 繁體中文研究出版庫。以經文、歷史文獻與證據界線為基礎的專題研究。', '',
             '文章全文及引用直接包含在 HTML 中，不需登入或執行 JavaScript；圖表互動另需 JavaScript。',
             '史料記載、作者詮釋與推測的區分請依各篇原文；引用時使用文章網址或章節永久連結。', '',
             '## 研究目錄', '']
    for r in records:
        lines.append(f'- [{r["title"]}]({r["url"]}): {r["description"]}')
    lines += ['', '## 機器可讀入口', '', f'- [含章節連結的 JSON 目錄]({BASE}catalog.json)', f'- [網站地圖]({BASE}sitemap.xml)', '']
    (ROOT / 'llms.txt').write_text('\n'.join(lines))
    print(f'Updated metadata and discovery files for {len(records)} pages.')


if __name__ == '__main__':
    main()
