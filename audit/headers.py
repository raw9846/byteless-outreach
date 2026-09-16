from typing import Dict, Any

SECURITY_HEADERS = [
    ("Strict-Transport-Security", "Forces HTTPS on all future requests — missing means downgrade/MITM exposure."),
    ("Content-Security-Policy", "Restricts what scripts/resources can load — missing leaves a wide XSS surface."),
    ("X-Content-Type-Options", "Blocks MIME-sniffing attacks — should be 'nosniff'."),
    ("X-Frame-Options", "Prevents clickjacking via iframe embedding."),
    ("Referrer-Policy", "Controls how much URL data leaks to third parties on outbound links."),
    ("Permissions-Policy", "Restricts browser feature access (camera, geolocation, etc.)."),
]


def check_headers(headers: Dict[str, str]) -> Dict[str, Any]:
    lower_headers = {k.lower(): v for k, v in (headers or {}).items()}

    present = []
    missing = []
    for name, why in SECURITY_HEADERS:
        if name.lower() in lower_headers:
            present.append(name)
        else:
            missing.append({"header": name, "why_it_matters": why})

    server = lower_headers.get("server", "")
    x_powered_by = lower_headers.get("x-powered-by", "")

    cookie_issues = []
    set_cookie = lower_headers.get("set-cookie", "")
    if set_cookie:
        if "secure" not in set_cookie.lower():
            cookie_issues.append("Cookie missing Secure flag")
        if "httponly" not in set_cookie.lower():
            cookie_issues.append("Cookie missing HttpOnly flag")

    return {
        "present": present,
        "missing": missing,
        "score": len(present),
        "max_score": len(SECURITY_HEADERS),
        "server_disclosed": server or None,
        "x_powered_by_disclosed": x_powered_by or None,
        "cookie_issues": cookie_issues,
    }
