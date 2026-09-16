import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Dict, List

CAREER_PATHS = [
    "/careers", "/jobs", "/work-with-us", "/join-us", "/join-our-team",
    "/about/careers", "/company/careers", "/hiring", "/open-positions",
    "/opportunities", "/about/jobs",
]

TECH_KEYWORDS = [
    "developer", "engineer", "devops", "data scientist", "cloud", "architect",
    "software", "platform", "infrastructure", "backend", "frontend", "fullstack",
    "api", "database", "security", "automation", "cto", "it manager",
]

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}


def find_job_signals(html: str, domain: str) -> Dict:
    base_url = f"https://{domain}"
    soup = BeautifulSoup(html, "lxml")

    # Look for careers link on homepage
    careers_link = None
    for a in soup.find_all("a", href=True):
        href = a.get("href", "").lower()
        text = a.text.lower()
        if any(kw in href or kw in text for kw in ["career", "jobs", "hiring", "join us", "work with"]):
            careers_link = urljoin(base_url, a["href"])
            break

    # Try careers pages
    pages_to_try = ([careers_link] if careers_link else []) + [
        urljoin(base_url, path) for path in CAREER_PATHS[:6]
    ]

    careers_found = False
    tech_signals: List[str] = []

    for url in pages_to_try:
        try:
            r = requests.get(url, timeout=8, headers=HEADERS)
            if r.status_code == 200 and len(r.text) > 300:
                careers_found = True
                text = BeautifulSoup(r.text, "lxml").get_text().lower()
                tech_signals = list({kw for kw in TECH_KEYWORDS if kw in text})
                break
        except Exception:
            continue

    return {
        "careers_page_found": careers_found,
        "tech_hiring_signals": tech_signals[:8],
        "is_hiring_tech": len(tech_signals) > 0,
    }
