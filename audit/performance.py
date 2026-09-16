import requests
from typing import Dict, Any

PAGESPEED_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


def _fetch_pagespeed(url: str, strategy: str, api_key: str) -> Dict:
    params = {
        "url": url,
        "strategy": strategy,
        "category": ["performance", "accessibility", "best-practices", "seo"],
    }
    if api_key:
        params["key"] = api_key

    resp = requests.get(PAGESPEED_URL, params=params, timeout=35)
    return resp.json()


def get_performance_score(url: str, api_key: str = "") -> Dict[str, Any]:
    result = {
        "mobile": {},
        "desktop": {},
        "opportunities": [],
        "diagnostics": [],
        "error": None,
    }

    try:
        for strategy in ["mobile", "desktop"]:
            data = _fetch_pagespeed(url, strategy, api_key)
            lh = data.get("lighthouseResult", {})
            categories = lh.get("categories", {})
            audits = lh.get("audits", {})

            scores = {
                cat: round((info.get("score") or 0) * 100)
                for cat, info in categories.items()
            }

            metrics = {}
            for k in ["first-contentful-paint", "largest-contentful-paint",
                      "total-blocking-time", "cumulative-layout-shift",
                      "speed-index", "interactive"]:
                if k in audits:
                    metrics[k] = audits[k].get("displayValue", "N/A")

            result[strategy] = {"scores": scores, "metrics": metrics}

            # Opportunities (only extract from mobile — more impactful)
            if strategy == "mobile":
                opportunity_ids = [
                    "render-blocking-resources",
                    "unused-javascript",
                    "unused-css-rules",
                    "uses-optimized-images",
                    "uses-next-gen-formats",
                    "uses-responsive-images",
                    "efficiently-encode-images",
                    "uses-text-compression",
                    "uses-long-cache-ttl",
                    "reduce-server-response-times",
                    "unminified-javascript",
                    "unminified-css",
                    "no-document-write",
                ]
                for oid in opportunity_ids:
                    audit = audits.get(oid)
                    if audit and audit.get("score") is not None and audit["score"] < 0.9:
                        savings = audit.get("details", {}).get("overallSavingsMs")
                        desc = audit.get("title", oid)
                        entry = {"issue": desc}
                        if savings:
                            entry["potential_saving_ms"] = round(savings)
                        result["opportunities"].append(entry)

                # Diagnostics
                diagnostic_ids = [
                    "uses-passive-event-listeners",
                    "no-document-write",
                    "third-party-summary",
                    "bootup-time",
                    "mainthread-work-breakdown",
                    "dom-size",
                ]
                for did in diagnostic_ids:
                    audit = audits.get(did)
                    if audit and audit.get("score") is not None and audit["score"] < 0.9:
                        result["diagnostics"].append({
                            "issue": audit.get("title", did),
                            "value": audit.get("displayValue", ""),
                        })

    except Exception as e:
        result["error"] = str(e)

    # Backward-compatible flat scores field (uses mobile)
    result["scores"] = result["mobile"].get("scores", {})
    result["metrics"] = result["mobile"].get("metrics", {})

    return result
