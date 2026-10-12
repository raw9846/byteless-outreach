import re
import requests
from typing import Dict

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}


def check_catalog_depth(domain: str) -> Dict:
    """Estimate product catalog size via two independent signals:
    Shopify-style products.json (page 1 count, capped at 250) and the
    number of paginated product-sitemap files (a rough proxy for catalog
    depth on non-Shopify platforms that shard sitemap.xml by product).

    Either signal can legitimately come back empty on a platform that
    doesn't expose it — that's recorded as a status code, not treated as
    "zero products".
    """
    result: Dict = {}
    base = f"https://{domain}"

    try:
        r = requests.get(f"{base}/products.json?limit=250", timeout=10, headers=HEADERS)
        if r.status_code == 200:
            try:
                products = r.json().get("products", [])
                result["products_json_page1_count"] = len(products)
            except ValueError:
                result["products_json_status"] = "200 but not valid JSON (likely not Shopify)"
        else:
            result["products_json_status"] = r.status_code
    except Exception as e:
        result["products_json_status"] = f"error: {e}"

    try:
        r = requests.get(f"{base}/sitemap.xml", timeout=10, headers=HEADERS)
        if r.status_code == 200:
            product_sitemaps = set(re.findall(r"sitemap_products_\d+\.xml", r.text))
            result["product_sitemap_file_count"] = len(product_sitemaps)
        else:
            result["sitemap_status"] = r.status_code
    except Exception as e:
        result["sitemap_status"] = f"error: {e}"

    return result
