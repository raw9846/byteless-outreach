import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Dict, List


def _visible_text(html: str) -> str:
    """Page text with <script>/<style> contents stripped — BeautifulSoup's
    get_text() otherwise includes raw JS/CSS source, which produces false
    keyword matches (e.g. "cto" inside "querySelectorAll").
    """
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return soup.get_text().lower()


def _find_whole_word_matches(text: str, keywords: List[str]) -> List[str]:
    return [kw for kw in keywords if re.search(r"\b" + re.escape(kw) + r"\b", text)]

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
                text = _visible_text(r.text)
                tech_signals = _find_whole_word_matches(text, TECH_KEYWORDS)
                break
        except Exception:
            continue

    return {
        "careers_page_found": careers_found,
        "tech_hiring_signals": tech_signals[:8],
        "is_hiring_tech": len(tech_signals) > 0,
    }


TEAM_PATHS = [
    "/about", "/about-us", "/team", "/our-team", "/company", "/about/team",
    "/who-we-are", "/meet-the-team", "/leadership",
]

ENGINEERING_TITLE_KEYWORDS = [
    "software engineer", "software developer", "web developer", "developer",
    "cto", "chief technology officer", "vp of engineering", "head of engineering",
    "director of engineering", "engineering lead", "platform engineer",
    "backend engineer", "frontend engineer", "full stack", "devops engineer",
]


def find_team_engineering_signals(html: str, domain: str) -> Dict:
    """Check the site's own About/Team page for listed staff with engineering
    titles — i.e. do they already have in-house software people, as opposed
    to `find_job_signals` above which only checks if they're currently
    *hiring* for tech roles. Same static-HTML caveat applies: a team page
    that's JS-rendered (e.g. loaded from a CMS via client-side fetch) won't
    be visible here.
    """
    base_url = f"https://{domain}"
    soup = BeautifulSoup(html, "lxml")

    team_link = None
    for a in soup.find_all("a", href=True):
        href = a.get("href", "").lower()
        text = a.text.lower()
        if any(kw in href or kw in text for kw in ["about", "team", "who we are", "leadership"]):
            team_link = urljoin(base_url, a["href"])
            break

    pages_to_try = ([team_link] if team_link else []) + [
        urljoin(base_url, path) for path in TEAM_PATHS
    ]

    team_page_found = False
    matched_titles: List[str] = []

    for url in pages_to_try:
        try:
            r = requests.get(url, timeout=8, headers=HEADERS)
            if r.status_code == 200 and len(r.text) > 300:
                team_page_found = True
                text = _visible_text(r.text)
                matched_titles = _find_whole_word_matches(text, ENGINEERING_TITLE_KEYWORDS)
                break
        except Exception:
            continue

    return {
        "team_page_found": team_page_found,
        "engineering_titles_found": matched_titles[:8],
        "has_in_house_engineering_team": len(matched_titles) > 0,
    }
