from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from typing import Dict, Any

LEGACY_SIGNALS = [
    "jquery-1.", "jquery-2.", "jquery.min.js", "jquery-migrate",
    "bootstrap-2.", "bootstrap-3.", "prototype.js", "mootools",
    "flash", ".swf", "silverlight",
]

MODERN_FRAMEWORK_SIGNALS = [
    "__next", "_next/static", "react.production", "vue.min.js",
    "angular", "svelte", "gatsby-", "__nuxt",
]

APP_STORE_SIGNALS = [
    "apps.apple.com", "itunes.apple.com", "app store",
    "play.google.com", "google play",
]

SEARCH_SIGNALS = [
    "algolia", "elasticsearch", "typesense", "doofinder",
    "searchspring", "hawksearch", "searchanise",
    'type="search"', 'name="search"', 'name="q"', 'placeholder="search"',
]

ADVANCED_SEARCH_SIGNALS = [
    "algolia", "elasticsearch", "typesense", "doofinder",
    "searchspring", "hawksearch",
]

DASHBOARD_SIGNALS = [
    "/dashboard", "/admin", "/portal", "/app", "/account",
    "dashboard", "my account", "client area",
]

CUSTOM_APP_INDICATORS = [
    "api.php", "/api/v", "rest/v", "graphql",
    "webpack", "chunk.", "bundle.js",
]

BASIC_CMS_PLATFORMS = ["wix.com", "wixstatic.com", "squarespace.com", "weebly.com", "godaddy"]


def check_webapp_signals(html: str, base_url: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")
    html_lower = html.lower()
    all_text = html_lower

    gaps = []
    signals = {}

    # Legacy tech stack
    is_legacy = any(s in all_text for s in LEGACY_SIGNALS)
    is_modern = any(s in all_text for s in MODERN_FRAMEWORK_SIGNALS)
    signals["legacy_tech"] = is_legacy
    signals["modern_framework"] = is_modern
    if is_legacy and not is_modern:
        gaps.append({
            "gap": "Legacy frontend tech (jQuery/old Bootstrap era)",
            "impact": "Slow development velocity, hard to hire for, growing technical debt — every new feature takes longer and breaks more things",
            "opportunity": "Migrate to a modern React/Next.js stack — faster builds, better developer experience, significantly improved performance",
        })

    # Built on basic website builder (not appropriate for business complexity)
    is_basic_builder = any(s in all_text for s in BASIC_CMS_PLATFORMS)
    signals["basic_website_builder"] = is_basic_builder
    if is_basic_builder:
        gaps.append({
            "gap": "Business running on a basic website builder (Wix/Squarespace/GoDaddy)",
            "impact": "Severely limited customisation, poor performance, no ability to build custom features or integrations as the business grows",
            "opportunity": "Rebuild on a proper stack (Next.js + headless CMS or custom) to unlock custom features, integrations, and real scalability",
        })

    # No mobile app
    has_app = any(s in all_text for s in APP_STORE_SIGNALS)
    signals["has_mobile_app"] = has_app
    # Only flag if they're a service/ecommerce business that would benefit from an app
    if not has_app:
        signals["mobile_app_gap"] = True

    # Search quality
    has_any_search = any(s in all_text for s in SEARCH_SIGNALS)
    has_advanced_search = any(s in all_text for s in ADVANCED_SEARCH_SIGNALS)
    signals["has_search"] = has_any_search
    signals["has_advanced_search"] = has_advanced_search
    if has_any_search and not has_advanced_search:
        gaps.append({
            "gap": "Basic search with no advanced search / filtering capability",
            "impact": "Customers can't find products efficiently — poor product discovery directly reduces conversion, especially on larger catalogues",
            "opportunity": "Integrate Algolia or build a custom search with faceted filtering, autocomplete, and relevance tuning",
        })

    # No customer/account area
    has_account = any(s in all_text for s in DASHBOARD_SIGNALS)
    signals["has_account_area"] = has_account

    # Custom app signals (already has some custom development)
    has_custom = any(s in all_text for s in CUSTOM_APP_INDICATORS)
    signals["has_custom_app_signals"] = has_custom

    # Check if key pages exist
    key_pages = {}
    for path, label in [("/about", "about"), ("/pricing", "pricing"), ("/blog", "blog"), ("/faq", "faq")]:
        try:
            r = requests.head(urljoin(base_url, path), timeout=5, allow_redirects=True)
            key_pages[label] = r.status_code == 200
        except Exception:
            key_pages[label] = False

    signals["key_pages"] = key_pages

    # Blog freshness (if blog exists, check last post date)
    blog_freshness = None
    if key_pages.get("blog"):
        try:
            r = requests.get(urljoin(base_url, "/blog"), timeout=8)
            blog_soup = BeautifulSoup(r.text, "lxml")
            # Look for date tags
            for tag in blog_soup.find_all(["time", "span"], attrs={"datetime": True}):
                blog_freshness = tag.get("datetime", "")[:10]
                break
            if not blog_freshness:
                # Look for common date patterns in text
                import re
                date_pattern = re.compile(r'\b(20\d{2}[-/]\d{2}[-/]\d{2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2},?\s+20\d{2})\b')
                match = date_pattern.search(r.text)
                if match:
                    blog_freshness = match.group(0)
        except Exception:
            pass

    signals["blog_last_post"] = blog_freshness

    # No pricing page — common friction point
    if not key_pages.get("pricing"):
        gaps.append({
            "gap": "No pricing page",
            "impact": "Prospects can't self-qualify on budget — every lead requires a manual sales conversation before the first number is discussed",
            "opportunity": "Build a pricing page with tiered plans or a transparent pricing calculator to pre-qualify leads",
        })

    return {
        "signals": signals,
        "gaps": gaps,
        "gap_count": len(gaps),
    }
