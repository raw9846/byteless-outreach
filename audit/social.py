from bs4 import BeautifulSoup
from typing import Dict

SOCIAL_PATTERNS = {
    "linkedin": ["linkedin.com/company", "linkedin.com/in"],
    "twitter": ["twitter.com/", "x.com/"],
    "instagram": ["instagram.com/"],
    "facebook": ["facebook.com/"],
    "youtube": ["youtube.com/"],
}


def check_social_presence(html: str) -> Dict:
    soup = BeautifulSoup(html, "lxml")
    links_str = " ".join(a.get("href", "") for a in soup.find_all("a", href=True)).lower()
    html_lower = html.lower()

    found = {
        platform: any(p in links_str or p in html_lower for p in patterns)
        for platform, patterns in SOCIAL_PATTERNS.items()
    }

    missing = [p for p, exists in found.items() if not exists]

    return {
        "platforms": found,
        "missing": missing,
        "score": sum(found.values()),
        "max_score": len(SOCIAL_PATTERNS),
    }
