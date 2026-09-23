"""Integration checks for published files, navigation, and Markdown migration."""
from html.parser import HTMLParser
from pathlib import Path
import runpy
import unittest
from urllib.parse import unquote, urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE = runpy.run_path(str(ROOT / 'scripts/site.py'))
build, PAGES, OUTPUT = SITE['build'], SITE['PAGES'], SITE['OUTPUT']


class Document(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links = []
        self.ids = set()
        self.current = []
        self.headings = 0
        self.images = []
        self.stack = []
        self.invalid_paragraphs = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {'div', 'h2', 'h3', 'ul'} and 'p' in self.stack:
            self.invalid_paragraphs.append(tag)
        if tag not in {'meta', 'link', 'img', 'br', 'hr', 'input'}:
            self.stack.append(tag)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        if tag == 'h1':
            self.headings += 1
        if attrs.get('aria-current') == 'page':
            self.current.append(attrs.get('href'))
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append(attrs[key])
        if tag == 'img':
            self.images.append(attrs)

    def handle_endtag(self, tag):
        if tag in self.stack:
            self.stack = self.stack[:len(self.stack) - 1 - self.stack[::-1].index(tag)]


class SiteIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build()

    def validate_links(self, base=''):
        for path in OUTPUT.rglob('*.html'):
            html = path.read_text(encoding='utf-8')
            doc = Document(html)
            route = '/' + path.relative_to(OUTPUT).as_posix()
            for link in doc.links:
                parsed = urlparse(link)
                if parsed.scheme or parsed.netloc:
                    continue
                resolved = urlparse(urljoin(base + route, link))
                local = unquote(resolved.path)
                if base:
                    self.assertTrue(local.startswith(base + '/'), (path, link))
                    local = local[len(base):]
                target = OUTPUT / local.lstrip('/')
                if target.is_dir():
                    target /= 'index.html'
                self.assertTrue(target.is_file(), f'{path}: missing {link}')
                if resolved.fragment and target.suffix == '.html':
                    self.assertIn(unquote(resolved.fragment), Document(target.read_text(encoding='utf-8')).ids)

    def test_all_internal_links_and_assets_exist(self):
        self.validate_links()

    def test_independent_pages_have_one_heading_and_active_tab(self):
        for page in PAGES:
            html = (OUTPUT / page['slug'] / 'index.html').read_text(encoding='utf-8')
            doc = Document(html)
            self.assertEqual(doc.headings, 1, page['slug'])
            self.assertEqual(doc.current, ['/' + page['slug'] + ('/' if page['slug'] else '')])
            self.assertFalse(doc.invalid_paragraphs, (page['slug'], doc.invalid_paragraphs))
            self.assertNotIn('markdown="', html)
            self.assertNotIn('**Zelun', html)
            for img in doc.images:
                self.assertTrue(img.get('alt'))

    def test_migrated_academic_record(self):
        publications = (OUTPUT / 'publications/index.html').read_text(encoding='utf-8')
        self.assertEqual(publications.count('class="paper-box"'), 4)
        self.assertEqual(publications.count('class="paper-box-text"'), 4)
        for marker in ('11353523', '11353856', '11353552', 'science.aee6277', 's41928-025-01534-8', 's41928-025-01405-2', 's41467-024-45923-7', 'PiMM-NoC', '617.7 TOPS/W'):
            self.assertIn(marker, publications)
        self.assertEqual((OUTPUT / 'news/index.html').read_text(encoding='utf-8').count('<li>'), 17)
        self.assertEqual((OUTPUT / 'talks/index.html').read_text(encoding='utf-8').count('<li>'), 5)

    def test_build_is_clean_and_only_publishes_site_files(self):
        stale = OUTPUT / 'stale.html'
        stale.write_text('old output', encoding='utf-8')
        build()
        self.assertFalse(stale.exists())
        for excluded in ('content', 'templates', 'scripts', 'Gemfile', 'assets/js/main.min.js', 'images/redketchup.zip'):
            self.assertFalse((OUTPUT / excluded).exists())
        self.assertTrue((OUTPUT / '.nojekyll').exists())
        self.assertTrue((OUTPUT / '404.html').exists())
        self.assertIn('https://higgsbose.github.io/publications/', (OUTPUT / 'sitemap.xml').read_text())

    def test_project_site_prefix(self):
        try:
            build('/personal-page')
            self.validate_links('/personal-page')
            self.assertIn('https://higgsbose.github.io/personal-page/', (OUTPUT / 'index.html').read_text(encoding='utf-8'))
        finally:
            build()


if __name__ == '__main__':
    unittest.main()
