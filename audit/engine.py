import requests
from typing import Dict, Any, Tuple

from .tech_stack import detect_tech_stack
from .performance import get_performance_score
from .seo import analyze_seo
from .jobs import find_job_signals
from .social import check_social_presence
from .reviews import get_review_data
from .automation import find_automation_gaps
from .integrations import find_integration_gaps
from .webapp import check_webapp_signals
from .internal_systems import check_internal_systems
from .headers import check_headers
from enrichment.apollo import enrich_organization

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}


def fetch_page(url: str) -> Tuple[str, dict, int]:
    try:
        r = requests.get(url, timeout=12, headers=HEADERS, allow_redirects=True)
        return r.text, dict(r.headers), r.status_code
    except Exception:
        return "", {}, 0


def run_audit(domain: str, pagespeed_api_key: str = "", company_name: str = "") -> Dict[str, Any]:
    url = f"https://{domain}"
    html, headers, status = fetch_page(url)

    if status != 200:
        url = f"https://www.{domain}"
        html, headers, status = fetch_page(url)

    if status != 200:
        url = f"http://{domain}"
        html, headers, status = fetch_page(url)

    result: Dict[str, Any] = {
        "domain": domain,
        "url": url,
        "reachable": status == 200,
        "status_code": status,
    }

    # Independent of site reachability — firmographic data comes from Apollo, not the scrape
    result["company_data"] = enrich_organization(domain, company_name or None)
    result["headers"] = check_headers(headers)

    if not result["reachable"]:
        return result

    result["tech_stack"] = detect_tech_stack(html, headers)
    result["performance"] = get_performance_score(url, pagespeed_api_key)
    result["seo"] = analyze_seo(html, url)
    result["jobs"] = find_job_signals(html, domain)
    result["social"] = check_social_presence(html)
    result["reviews"] = get_review_data(domain)
    result["automation"] = find_automation_gaps(html, domain)
    result["integrations"] = find_integration_gaps(html)
    result["webapp"] = check_webapp_signals(html, url)
    result["internal_systems"] = check_internal_systems(html, url)

    return result
