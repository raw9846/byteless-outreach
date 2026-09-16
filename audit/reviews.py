import requests
from bs4 import BeautifulSoup
from typing import Dict

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get_review_data(domain: str) -> Dict:
    clean = domain.replace("www.", "")
    result = {"trustpilot": None, "error": None}

    try:
        url = f"https://www.trustpilot.com/review/{clean}"
        r = requests.get(url, timeout=10, headers=HEADERS)

        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "lxml")

            # Try multiple selectors for rating
            rating = None
            for sel in [
                {"data-rating-typography": True},
                {"class": lambda c: c and "star-rating" in " ".join(c) if c else False},
            ]:
                el = soup.find("span", sel)
                if el:
                    rating = el.text.strip()
                    break

            # Try to find review count
            count_el = soup.find("span", {"data-reviews-count-typography": True})
            review_count = count_el.text.strip() if count_el else None

            result["trustpilot"] = {
                "exists": True,
                "url": url,
                "rating": rating or "profile exists",
                "review_count": review_count,
            }
        elif r.status_code == 404:
            result["trustpilot"] = {"exists": False}

    except Exception as e:
        result["error"] = str(e)

    return result
