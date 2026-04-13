#!/usr/bin/env python3
"""
build.py — Sync page content from thefriendshipclass.com WordPress REST API
           into the static evolveWithMoni GitHub Pages site.

Usage:
  python3 build.py                             # sync all mapped pages
  python3 build.py --list-slugs               # print all slugs from API (dry run)
  python3 build.py --page about               # sync one page by slug
  python3 build.py --download-images          # sync + download all WP images locally
  python3 build.py --page about --download-images
"""

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API_BASE = "https://thefriendshipclass.com/wp-json/wp/v2"
WP_DOMAIN = "https://thefriendshipclass.com"
REPO_ROOT = Path(__file__).parent

# Map WP slugs → local HTML files.
# Run --list-slugs first to confirm exact slugs from the live site.
SLUG_MAP = {
    "home":                                   "index.html",
    "about":                                  "about.html",
    "winning-in-friendship-class":            "friendship-class.html",
    "true-accountability-program-community":  "accountability.html",
    "events":                                 "events.html",
    "networking":                             "networking.html",
    "packages":                               "packages.html",
    "testimonials":                           "testimonials.html",
    "frequently-asked-questions":             "faq.html",
    "contact":                                "contact.html",
    "privacy-policy":                         "privacy-policy.html",
}

# Rewrite internal WP links → local HTML paths
LINK_MAP = {
    "https://thefriendshipclass.com/about/":                                  "about.html",
    "https://thefriendshipclass.com/winning-in-friendship-class/":            "friendship-class.html",
    "https://thefriendshipclass.com/true-accountability-program-community/":  "accountability.html",
    "https://thefriendshipclass.com/events/":                                 "events.html",
    "https://thefriendshipclass.com/networking/":                             "networking.html",
    "https://thefriendshipclass.com/packages/":                               "packages.html",
    "https://thefriendshipclass.com/testimonials/":                           "testimonials.html",
    "https://thefriendshipclass.com/frequently-asked-questions/":             "faq.html",
    "https://thefriendshipclass.com/contact/":                                "contact.html",
    "https://thefriendshipclass.com/privacy-policy/":                         "privacy-policy.html",
    "https://thefriendshipclass.com/":                                        "index.html",
}


def fetch_pages() -> list:
    url = f"{API_BASE}/pages?per_page=100&_fields=slug,title,content,status"
    req = urllib.request.Request(url, headers={"User-Agent": "evolveWithMoni-build/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def clean_elementor(html: str) -> str:
    """Remove Elementor scaffolding; keep semantic HTML."""
    # Remove data-elementor-* attributes
    html = re.sub(r'\s+data-elementor-[a-z-]+="[^"]*"', "", html)
    # Remove elementor-* tokens from class attributes
    html = re.sub(r"\belementor(?:-[a-z0-9_-]+)?\b\s*", "", html)
    # Collapse empty class attributes
    html = re.sub(r'\s+class="\s*"', "", html)
    return html


def rewrite_links(html: str) -> str:
    for wp_url, local in LINK_MAP.items():
        html = html.replace(f'href="{wp_url}"', f'href="{local}"')
    return html


def sanitize_filename(url_path: str) -> str:
    """Derive a safe local filename from a URL path component."""
    name = urllib.parse.unquote(os.path.basename(url_path))
    name = re.sub(r"[^\w\-.]", "-", name)   # replace unsafe chars with -
    name = re.sub(r"-{2,}", "-", name)       # collapse consecutive dashes
    return name.strip("-")


def download_image(url: str, images_dir: Path) -> str:
    """Download url into images_dir; return local relative path.

    Skips the download if the file already exists (idempotent).
    Returns the original url unchanged if the download fails.
    """
    parsed = urllib.parse.urlparse(url)
    filename = sanitize_filename(parsed.path)
    dest = images_dir / filename
    if not dest.exists():
        # Percent-encode the path so urllib handles filenames with spaces.
        safe_url = parsed._replace(path=urllib.parse.quote(parsed.path)).geturl()
        req = urllib.request.Request(safe_url, headers={"User-Agent": "evolveWithMoni-build/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                dest.write_bytes(resp.read())
            print(f"    ↓  images/{filename}")
        except Exception as exc:
            print(f"    ✗  {filename}: {exc}")
            return url
    return f"images/{filename}"


def localize_images(html: str, images_dir: Path) -> str:
    """Download all WP-hosted images and rewrite src to local paths.

    srcset attributes are stripped entirely: since src is now local, the
    browser uses it as the sole source, avoiding the space-in-filename
    ambiguity that srcset URL parsing introduces.
    """
    images_dir.mkdir(parents=True, exist_ok=True)

    def replace_src(m: re.Match) -> str:
        return f'src="{download_image(m.group(1), images_dir)}"'

    html = re.sub(rf'src="({re.escape(WP_DOMAIN)}/[^"]+)"', replace_src, html)
    html = re.sub(r'\s+srcset="[^"]*"', "", html)
    return html


def inject_content(html_file: Path, content: str) -> None:
    original = html_file.read_text(encoding="utf-8")
    block = f"\n<!-- MAIN (generated by build.py) -->\n{content}\n<!-- /MAIN -->\n\n"
    # Match from closing site-nav tag up to (but not including) the footer element.
    # Use a lambda replacement to prevent re.sub from interpreting backslashes
    # in the content string (e.g. \u sequences from Elementor JS snippets).
    replacement = f"</nav>\n{block}\n"
    updated = re.sub(
        r"</nav>.*?(?=<footer\b)",
        lambda _: replacement,
        original,
        count=1,
        flags=re.DOTALL,
    )
    if updated == original:
        print(f"  ⚠  {html_file.name}: no change (check anchor tags)")
        return
    html_file.write_text(updated, encoding="utf-8")
    print(f"  ✓  {html_file.name}")


def process_page(page: dict, download_images: bool = False) -> None:
    slug = page["slug"]
    if slug not in SLUG_MAP:
        print(f"  –  unmapped: {slug}")
        return
    html_file = REPO_ROOT / SLUG_MAP[slug]
    if not html_file.exists():
        print(f"  ✗  missing file: {html_file}")
        return
    content = page["content"]["rendered"]
    content = clean_elementor(content)
    content = rewrite_links(content)
    if download_images:
        content = localize_images(content, REPO_ROOT / "images")
    inject_content(html_file, content)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--list-slugs",
        action="store_true",
        help="Print all slugs from API without writing files",
    )
    parser.add_argument("--page", metavar="SLUG", help="Sync a single page by slug")
    parser.add_argument(
        "--download-images",
        action="store_true",
        help="Download WP-hosted images to images/ and rewrite src/srcset to local paths",
    )
    args = parser.parse_args()

    print("Fetching pages from WP REST API…")
    try:
        pages = fetch_pages()
    except Exception as exc:
        print(f"Error fetching API: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.list_slugs:
        print(f"\n{len(pages)} pages found:\n")
        for p in pages:
            mapped = SLUG_MAP.get(p["slug"], "(unmapped)")
            print(f"  {p['slug']:<40} → {mapped}")
        return

    if args.page:
        pages = [p for p in pages if p["slug"] == args.page]
        if not pages:
            print(f"Slug '{args.page}' not found in API.", file=sys.stderr)
            sys.exit(1)

    print(f"\nProcessing {len(pages)} page(s)…\n")
    for page in pages:
        process_page(page, download_images=args.download_images)
    print("\nDone.")


if __name__ == "__main__":
    main()
