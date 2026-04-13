#!/usr/bin/env python3
"""
build.py — Mirror thefriendshipclass.com pages as static HTML for GitHub Pages.

Fetches each page's full rendered HTML, downloads CSS assets locally,
rewrites internal links to local .html paths, strips the WordPress admin
bar, and optionally downloads images.

Usage:
  python3 build.py                    # mirror all pages
  python3 build.py --page about       # mirror one page (dest filename stem)
  python3 build.py --download-images  # also download images locally
  python3 build.py --list-pages       # show the page map and exit
"""

import argparse
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

WP_DOMAIN = "https://thefriendshipclass.com"
REPO_ROOT = Path(__file__).parent

# Source URL → destination filename
PAGE_MAP = {
    f"{WP_DOMAIN}/":                                        "index.html",
    f"{WP_DOMAIN}/about/":                                  "about.html",
    f"{WP_DOMAIN}/winning-in-friendship-class/":            "friendship-class.html",
    f"{WP_DOMAIN}/true-accountability-program-community/":  "accountability.html",
    f"{WP_DOMAIN}/events/":                                 "events.html",
    f"{WP_DOMAIN}/networking/":                             "networking.html",
    f"{WP_DOMAIN}/packages/":                               "packages.html",
    f"{WP_DOMAIN}/testimonials/":                           "testimonials.html",
    f"{WP_DOMAIN}/frequently-asked-questions/":             "faq.html",
    f"{WP_DOMAIN}/contact/":                                "contact.html",
    f"{WP_DOMAIN}/privacy-policy/":                         "privacy-policy.html",
}

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; evolveWithMoni-build/2.0)"}

# Keep stylesheets from these domains as remote CDN links (not downloaded)
CDN_PASSTHROUGH = ("fonts.googleapis.com", "fonts.gstatic.com")


# ── Network helpers ───────────────────────────────────────────────────────────

def fetch_html(url: str) -> str:
    safe_url = urllib.parse.quote(url, safe=":/?=&#%")
    req = urllib.request.Request(safe_url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")


def sanitize_filename(name: str) -> str:
    name = urllib.parse.unquote(name)
    name = re.sub(r"[^\w\-.]", "-", name)
    name = re.sub(r"-{2,}", "-", name)
    return name.strip("-")


def download_asset(url: str, dest_dir: Path, label: str) -> str:
    """Download url to dest_dir; return local relative path. Skip if exists."""
    parsed = urllib.parse.urlparse(url)
    filename = sanitize_filename(parsed.path.replace("/", "-").lstrip("-"))
    dest = dest_dir / filename
    if not dest.exists():
        safe_url = parsed._replace(path=urllib.parse.quote(parsed.path)).geturl()
        req = urllib.request.Request(safe_url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                dest.write_bytes(resp.read())
            print(f"    ↓  {label}/{filename}")
        except Exception as exc:
            print(f"    ✗  {filename}: {exc}")
            return url
    return f"{label}/{filename}"


# ── HTML transformations ──────────────────────────────────────────────────────

def rewrite_css_links(html: str, css_dir: Path) -> str:
    """Download stylesheet files and rewrite their href attributes to local paths."""
    def replace_link_tag(m: re.Match) -> str:
        tag = m.group(0)
        if "stylesheet" not in tag:
            return tag
        href_m = re.search(r'href=(["\'])([^"\']+)\1', tag)
        if not href_m:
            return tag
        href = href_m.group(2)
        if not href.startswith("http"):
            return tag
        parsed = urllib.parse.urlparse(href)
        if any(cdn in parsed.netloc for cdn in CDN_PASSTHROUGH):
            return tag  # keep Google Fonts etc. as CDN
        local = download_asset(href, css_dir, "css/vendor")
        return tag[: href_m.start(2)] + local + tag[href_m.end(2) :]

    return re.sub(r"<link\b[^>]+/?>", replace_link_tag, html)


def strip_wp_cruft(html: str) -> str:
    """Remove the WordPress admin bar and its injected top-margin style."""
    html = re.sub(
        r'<div\b[^>]+id=["\']wpadminbar["\'][^>]*>.*?</div>',
        "",
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r"<style[^>]*>\s*html\s*\{[^}]*margin-top\s*:\s*32px[^}]*\}.*?</style>",
        "",
        html,
        flags=re.DOTALL,
    )
    return html


def rewrite_internal_links(html: str) -> str:
    """Rewrite absolute WP page URLs in href attributes to local .html paths."""
    for source_url, dest_file in PAGE_MAP.items():
        html = html.replace(f'href="{source_url}"', f'href="{dest_file}"')
        html = html.replace(f"href='{source_url}'", f"href='{dest_file}'")
    return html


def localize_images(html: str, images_dir: Path) -> str:
    """Download WP-hosted images to images/ and rewrite <img> src attributes.

    Only <img> tags are affected — <script src> and other tags are left
    pointing to the original domain. srcset is stripped so the browser
    falls back to the now-local src, avoiding space-in-filename parsing issues.
    """
    images_dir.mkdir(parents=True, exist_ok=True)

    def replace_img(m: re.Match) -> str:
        before, url, after = m.group(1), m.group(2), m.group(3)
        local = download_asset(url, images_dir, "images")
        return f'<img{before}src="{local}"{after}>'

    # Match only src inside <img ...> tags; strip srcset in the same pass
    html = re.sub(
        rf'<img(\b[^>]*?)\bsrc="({re.escape(WP_DOMAIN)}/[^"]+)"([^>]*)>',
        replace_img,
        html,
    )
    html = re.sub(r'\s+srcset="[^"]*"', "", html)
    return html


# ── Page builder ──────────────────────────────────────────────────────────────

def build_page(
    source_url: str,
    dest_file: Path,
    css_dir: Path,
    images_dir: Path,
    download_images: bool = False,
) -> None:
    print(f"\n  {dest_file.name}  ←  {source_url}")
    try:
        html = fetch_html(source_url)
    except Exception as exc:
        print(f"  ✗  fetch failed: {exc}")
        return

    html = rewrite_css_links(html, css_dir)
    html = strip_wp_cruft(html)
    html = rewrite_internal_links(html)
    if download_images:
        html = localize_images(html, images_dir)

    dest_file.write_text(html, encoding="utf-8")
    print(f"  ✓  written ({len(html):,} bytes)")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--page",
        metavar="NAME",
        help="Mirror one page by destination filename stem (e.g. 'about')",
    )
    parser.add_argument(
        "--download-images",
        action="store_true",
        help="Download WP images to images/ and rewrite src attributes",
    )
    parser.add_argument(
        "--list-pages",
        action="store_true",
        help="Print the page map and exit",
    )
    args = parser.parse_args()

    if args.list_pages:
        print("\nPage map:\n")
        for src, dest in PAGE_MAP.items():
            print(f"  {src:<60} → {dest}")
        return

    css_dir = REPO_ROOT / "css" / "vendor"
    css_dir.mkdir(parents=True, exist_ok=True)
    images_dir = REPO_ROOT / "images"

    pages = list(PAGE_MAP.items())
    if args.page:
        target = args.page if args.page.endswith(".html") else f"{args.page}.html"
        pages = [(src, dest) for src, dest in pages if dest == target]
        if not pages:
            print(f"No page '{args.page}' in PAGE_MAP.", file=sys.stderr)
            sys.exit(1)

    print(f"Mirroring {len(pages)} page(s)…")
    for source_url, dest_filename in pages:
        build_page(
            source_url,
            REPO_ROOT / dest_filename,
            css_dir,
            images_dir,
            download_images=args.download_images,
        )
    print("\nDone.")


if __name__ == "__main__":
    main()
