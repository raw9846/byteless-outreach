import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Dict, Any


def analyze_seo(html: str, base_url: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")
    issues = []

    # Title
    title_tag = soup.find("title")
    title_text = title_tag.text.strip() if title_tag else None
    if not title_text:
        issues.append("Missing title tag")
    elif len(title_text) > 60:
        issues.append(f"Title too long ({len(title_text)} chars, max 60)")
    elif len(title_text) < 20:
        issues.append(f"Title too short ({len(title_text)} chars)")

    # Meta description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    desc_content = meta_desc.get("content", "").strip() if meta_desc else None
    if not desc_content:
        issues.append("Missing meta description")
    elif len(desc_content) > 160:
        issues.append("Meta description too long (>160 chars)")
    elif len(desc_content) < 50:
        issues.append("Meta description too short (<50 chars)")

    # H1
    h1_tags = soup.find_all("h1")
    if len(h1_tags) == 0:
        issues.append("No H1 tag found")
    elif len(h1_tags) > 1:
        issues.append(f"Multiple H1 tags ({len(h1_tags)} found — bad for SEO)")

    # Open Graph
    og_title = soup.find("meta", attrs={"property": "og:title"})
    og_image = soup.find("meta", attrs={"property": "og:image"})
    if not og_title:
        issues.append("Missing Open Graph tags (hurts social sharing previews)")

    # Schema markup
    schema = soup.find("script", attrs={"type": "application/ld+json"})

    # Images without alt text
    images = soup.find_all("img")
    no_alt = [img for img in images if not img.get("alt")]
    if no_alt:
        issues.append(f"{len(no_alt)} images missing alt text")

    # Canonical
    canonical = soup.find("link", attrs={"rel": "canonical"})

    # Sitemap check
    sitemap_ok = False
    try:
        r = requests.head(urljoin(base_url, "/sitemap.xml"), timeout=5)
        sitemap_ok = r.status_code == 200
    except Exception:
        pass
    if not sitemap_ok:
        issues.append("No sitemap.xml found")

    # Robots.txt
    robots_ok = False
    try:
        r = requests.head(urljoin(base_url, "/robots.txt"), timeout=5)
        robots_ok = r.status_code == 200
    except Exception:
        pass

    return {
        "title": title_text,
        "meta_description": desc_content,
        "h1_count": len(h1_tags),
        "has_og_tags": bool(og_title),
        "has_og_image": bool(og_image),
        "has_schema": bool(schema),
        "has_canonical": bool(canonical),
        "has_sitemap": sitemap_ok,
        "has_robots": robots_ok,
        "issues": issues,
        "issue_count": len(issues),
    }
