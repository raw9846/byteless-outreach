from typing import Dict, Any, List, Optional

import requests

from config import APOLLO_API_KEY

ENRICH_URL = "https://api.apollo.io/api/v1/organizations/enrich"
SEARCH_URL = "https://api.apollo.io/api/v1/mixed_people/api_search"
MATCH_URL = "https://api.apollo.io/api/v1/people/match"

# Apollo's person_titles filter on this endpoint is unreliable (silently
# ignored or over-broad fuzzy-matched) — so instead we pull the org's full
# indexed roster and rank it ourselves by title seniority.
SENIORITY_KEYWORDS = [
    (100, ["founder", "co-founder", "owner"]),
    (90, ["chief executive", " ceo"]),
    (50, ["vice president", " vp "]),  # must be checked before the generic "president" match below
    (80, ["president"]),
    (70, ["chief operating", " coo", "chief financial", " cfo", "chief technology", " cto"]),
    (60, ["managing director", "general manager"]),
    (40, ["director"]),
    (30, ["head of"]),
]


def _seniority_score(title: str) -> int:
    t = f" {(title or '').lower()} "
    for score, keywords in SENIORITY_KEYWORDS:
        if any(kw in t for kw in keywords):
            return score
    return 0


def enrich_organization(domain: str, company_name: Optional[str] = None) -> Dict[str, Any]:
    """Fetch firmographic company data from Apollo's Organization Enrichment API.

    Returns a dict with an 'error' key (and nothing else) if the API key is
    missing, the request fails, or no match is found — callers should treat
    that as "no enrichment available" rather than a hard failure.
    """
    if not APOLLO_API_KEY:
        return {"error": "APOLLO_API_KEY not set in .env"}

    params = {"domain": domain}
    if company_name:
        params["name"] = company_name

    try:
        resp = requests.get(
            ENRICH_URL,
            params=params,
            headers={"x-api-key": APOLLO_API_KEY, "Content-Type": "application/json"},
            timeout=15,
        )
        data = resp.json()
    except Exception as e:
        return {"error": str(e)}

    org = data.get("organization")
    if not org:
        return {"error": data.get("error") or "No match found"}

    return {
        "name": org.get("name"),
        "industry": org.get("industry"),
        "employee_count": org.get("estimated_num_employees"),
        "annual_revenue": org.get("annual_revenue"),
        "total_funding": org.get("total_funding"),
        "founded_year": org.get("founded_year"),
        "city": org.get("city"),
        "state": org.get("state"),
        "country": org.get("country"),
        "linkedin_url": org.get("linkedin_url"),
        "technologies": org.get("technology_names"),
        "headcount_6mo_growth": org.get("organization_headcount_six_month_growth"),
    }


def find_top_contact(domain: str) -> Dict[str, Any]:
    """Find and enrich the most senior contact Apollo has indexed for a domain.

    Two-step Apollo flow: search returns an obfuscated roster (no credit
    cost), then a single people/match call unlocks the best-ranked
    candidate's real email/LinkedIn (this step consumes a credit).

    Returns a dict with an 'error' key if the key is missing, the domain
    isn't indexed, or nothing could be enriched. Always includes a
    'confidence' note so low-seniority matches aren't mistaken for a
    confirmed decision-maker.
    """
    if not APOLLO_API_KEY:
        return {"error": "APOLLO_API_KEY not set in .env"}

    try:
        search_resp = requests.post(
            SEARCH_URL,
            headers={"x-api-key": APOLLO_API_KEY, "Content-Type": "application/json"},
            json={"q_organization_domains_list": [domain], "page": 1, "per_page": 25},
            timeout=15,
        )
        people: List[dict] = search_resp.json().get("people", [])
    except Exception as e:
        return {"error": str(e)}

    if not people:
        return {"error": "No contacts indexed for this domain in Apollo"}

    ranked = sorted(people, key=lambda p: _seniority_score(p.get("title", "")), reverse=True)
    best = ranked[0]
    best_score = _seniority_score(best.get("title", ""))

    try:
        match_resp = requests.post(
            MATCH_URL,
            headers={"x-api-key": APOLLO_API_KEY, "Content-Type": "application/json"},
            json={"id": best["id"]},
            timeout=15,
        )
        person = match_resp.json().get("person")
    except Exception as e:
        return {"error": str(e)}

    if not person:
        return {"error": "Search found a candidate but enrichment failed"}

    return {
        "name": person.get("name"),
        "title": person.get("title"),
        "email": person.get("email"),
        "email_status": person.get("email_status"),
        "linkedin_url": person.get("linkedin_url"),
        "confidence": "high" if best_score >= 80 else "medium" if best_score >= 40 else "low — no senior title found, best available contact",
    }
