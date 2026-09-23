"""Build and preview the same static files that GitHub Pages serves."""
from __future__ import annotations

import argparse
import hashlib
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
from urllib.parse import urlparse
from xml.sax.saxutils import escape

from jinja2 import Environment, FileSystemLoader, select_autoescape
import markdown

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "_site"
PAGES = [
    {"slug": "", "label": "About", "title": "Zelun Pan · Researcher", "number": "01"},
    {"slug": "news", "label": "News", "title": "News & updates", "number": "02"},
    {"slug": "publications", "label": "Publications", "title": "Publications", "number": "03"},
    {"slug": "talks", "label": "Talks", "title": "Talks & presentations", "number": "04"},
    {"slug": "projects", "label": "Projects", "title": "Selected projects", "number": "05"},
    {"slug": "cv", "label": "CV", "title": "Curriculum vitae", "number": "06"},
    {"slug": "life", "label": "Life", "title": "Life beyond the lab", "number": "07"},
]


def build(base_path: str = "", site_url: str = "https://higgsbose.github.io") -> None:
    base_path = "/" + base_path.strip("/") if base_path.strip("/") else ""
    parsed = urlparse(site_url)
    if parsed.scheme not in {"https", "http"} or not parsed.netloc:
        raise ValueError("--site-url must be an absolute HTTP(S) URL")
    if any(part in {".", ".."} for part in base_path.split("/")):
        raise ValueError("--base-path cannot contain dot segments")
    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=select_autoescape())
    env.globals["url"] = lambda path: f"{base_path}/{path.lstrip('/')}"
    env.globals["asset_url"] = lambda path: f"{base_path}/{path}?v={hashlib.sha256((ROOT / path).read_bytes()).hexdigest()[:12]}"
    profile = json.loads((ROOT / "content/profile.json").read_text(encoding="utf-8"))
    background = json.loads((ROOT / "content/background.json").read_text(encoding="utf-8"))
    # Never delete a symlink target or a directory outside this repository.
    if OUTPUT.resolve() != ROOT / "_site" or OUTPUT.is_symlink():
        raise ValueError("Refusing to replace an output directory outside the repository")
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()
    for name in ("css/site.css", "js/site.js", "images/paper.svg"):
        target = OUTPUT / "assets" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "assets" / name, target)
    shutil.copytree(ROOT / "images", OUTPUT / "images", ignore=shutil.ignore_patterns("*.zip"))
    (OUTPUT / "docs").mkdir(exist_ok=True)
    for name in ("潘泽伦_简历.pdf", "PanZelun_Resume.docx"):
        shutil.copy2(ROOT / "docs" / name, OUTPUT / "docs" / name)
    for page in PAGES:
        source = ROOT / "content" / f"{page['slug'] or 'about'}.md"
        content = markdown.markdown(source.read_text(encoding="utf-8"), extensions=["md_in_html", "tables", "attr_list"])
        # Authored legacy images and CV links work on user sites and project sites.
        content = content.replace('src="images/', f'src="{base_path}/images/').replace("src='images/", f"src='{base_path}/images/")
        content = content.replace('href="/docs/', f'href="{base_path}/docs/')
        route = f"{page['slug']}/" if page["slug"] else ""
        destination = OUTPUT / route
        destination.mkdir(exist_ok=True)
        canonical = f"{site_url.rstrip('/')}{base_path}/{route}"
        html = env.get_template("page.html").render(page=page, pages=PAGES, profile=profile, background=background, content=content, canonical=canonical)
        (destination / "index.html").write_text(html, encoding="utf-8")
    for alias in ("about/index.html", "about.html"):
        target = OUTPUT / alias
        target.parent.mkdir(exist_ok=True)
        target.write_text(env.get_template("redirect.html").render(target=f"{base_path}/"), encoding="utf-8")
    (OUTPUT / "404.html").write_text(env.get_template("404.html").render(pages=PAGES, profile=profile, page={"slug": "404", "title": "Page not found"}, canonical=""), encoding="utf-8")
    (OUTPUT / ".nojekyll").touch()
    urls = [f"{site_url.rstrip('/')}{base_path}/{p['slug'] + '/' if p['slug'] else ''}" for p in PAGES]
    (OUTPUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{escape(url)}</loc></url>" for url in urls) + "</urlset>\n", encoding="utf-8")
    (OUTPUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {site_url.rstrip('/')}{base_path}/sitemap.xml\n", encoding="utf-8")
    print(f"Built {len(PAGES)} pages in {OUTPUT}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["build", "serve"], nargs="?", default="build")
    parser.add_argument("--port", type=int, default=4000)
    parser.add_argument("--base-path", default="", help="Optional GitHub project path, e.g. /my-site")
    parser.add_argument("--site-url", default="https://higgsbose.github.io")
    args = parser.parse_args()
    if args.command == "serve" and args.base_path:
        parser.error("Preview uses the root path; use build to validate a project --base-path.")
    build(args.base_path, args.site_url)
    if args.command == "serve":
        handler = partial(SimpleHTTPRequestHandler, directory=str(OUTPUT))
        print(f"Preview: http://127.0.0.1:{args.port} (Ctrl+C to stop; rebuild after edits)", flush=True)
        with ThreadingHTTPServer(("127.0.0.1", args.port), handler) as server:
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                print("\nPreview stopped.")


if __name__ == "__main__":
    main()
