import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Dict, Any

# Detectable monitoring / observability tools (inject browser agents)
MONITORING_TOOLS = {
    "Sentry": ["sentry.io", "sentry_dsn", "sentry-browser"],
    "Datadog RUM": ["datadoghq.com", "rum.datadoghq", "datadog-rum"],
    "New Relic": ["newrelic.com", "newrelic.js", "nr-data.net"],
    "LogRocket": ["logrocket.com", "logrocket.js"],
    "Dynatrace": ["dynatrace.com", "dtrum"],
    "Bugsnag": ["bugsnag.com"],
    "Rollbar": ["rollbar.com"],
    "AppDynamics": ["appdynamics.com"],
}

# Workflow / process automation tools (some inject snippets or appear in forms)
WORKFLOW_TOOLS = {
    "Zapier": ["zapier.com", "hooks.zapier.com"],
    "Make (Integromat)": ["make.com", "integromat.com"],
    "n8n": ["n8n.io"],
    "Workato": ["workato.com"],
    "Tray.io": ["tray.io"],
    "Automate.io": ["automate.io"],
    "Power Automate": ["powerautomate.com", "flow.microsoft"],
    "Retool": ["retool.com"],
}

# BI / reporting tools
BI_TOOLS = {
    "Tableau": ["tableau.com", "tableau-public"],
    "Looker": ["looker.com"],
    "Power BI": ["powerbi.com", "app.powerbi"],
    "Metabase": ["metabase.com"],
    "Google Data Studio": ["datastudio.google", "lookerstudio.google"],
    "Sisense": ["sisense.com"],
    "Klipfolio": ["klipfolio.com"],
    "Chartio": ["chartio.com"],
    "Mode": ["app.mode.com"],
}

# Project management / ops tools (sometimes referenced in public pages)
OPS_TOOLS = {
    "Jira": ["jira.com", "atlassian.net/jira"],
    "Asana": ["asana.com"],
    "Monday.com": ["monday.com"],
    "ClickUp": ["clickup.com"],
    "Notion": ["notion.so", "notion.site"],
    "Confluence": ["confluence.atlassian"],
    "Linear": ["linear.app"],
    "Basecamp": ["basecamp.com"],
}

# Finance / billing / invoicing
FINANCE_TOOLS = {
    "QuickBooks": ["quickbooks.com", "intuit.com"],
    "Xero": ["xero.com"],
    "FreshBooks": ["freshbooks.com"],
    "Sage": ["sage.com"],
    "Zuora": ["zuora.com"],
    "Chargebee": ["chargebee.com"],
    "Paddle": ["paddle.com"],
    "Invoice Ninja": ["invoiceninja.com"],
}

# SaaS / API / developer signals
SAAS_SIGNALS = [
    "/api", "/api/v1", "/api/v2", "/docs", "/developer", "/developers",
    "developer.php", "api-docs", "swagger", "openapi", "graphql",
    "status.", "statuspage.io", "status page",
]

MULTI_TENANT_SIGNALS = [
    "workspace", "organisation", "tenant", "team-", "/teams/",
    "subdomain", "white-label", "whitelabel", "reseller",
    "manage your account", "switch account",
]


def check_internal_systems(html: str, base_url: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")
    html_lower = html.lower()
    links = " ".join(a.get("href", "") for a in soup.find_all("a", href=True)).lower()
    all_text = html_lower + " " + links

    detected = {}
    gaps = []

    # --- Detect what's present ---

    monitoring = [name for name, patterns in MONITORING_TOOLS.items()
                  if any(p.lower() in all_text for p in patterns)]
    detected["monitoring"] = monitoring

    workflow = [name for name, patterns in WORKFLOW_TOOLS.items()
                if any(p.lower() in all_text for p in patterns)]
    detected["workflow_automation"] = workflow

    bi_tools = [name for name, patterns in BI_TOOLS.items()
                if any(p.lower() in all_text for p in patterns)]
    detected["bi_reporting"] = bi_tools

    ops_tools = [name for name, patterns in OPS_TOOLS.items()
                 if any(p.lower() in all_text for p in patterns)]
    detected["project_management"] = ops_tools

    finance_tools = [name for name, patterns in FINANCE_TOOLS.items()
                     if any(p.lower() in all_text for p in patterns)]
    detected["finance_tools"] = finance_tools

    # SaaS / API signals
    has_api_docs = any(s in all_text for s in SAAS_SIGNALS[:8])
    has_multi_tenant = any(s in all_text for s in MULTI_TENANT_SIGNALS)
    detected["has_api_docs"] = has_api_docs
    detected["has_multi_tenant_signals"] = has_multi_tenant

    # Status page check
    has_status_page = False
    for path in ["/status", "status." + base_url.split("//")[-1].split("/")[0]]:
        try:
            r = requests.head(urljoin(base_url, "/status"), timeout=5)
            if r.status_code == 200:
                has_status_page = True
                break
        except Exception:
            pass
    detected["has_status_page"] = has_status_page

    # Job postings as internal tool signal (fetch from jobs module result if available)
    # Check for internal tool hiring signals in the HTML directly
    internal_hiring_signals = []
    tech_keywords = [
        "zapier", "make.com", "power automate", "tableau", "looker", "power bi",
        "salesforce admin", "netsuite", "sap", "oracle", "dynamics 365",
        "data engineer", "data analyst", "business analyst", "devops", "sre",
        "platform engineer", "internal tools", "back office",
    ]
    for kw in tech_keywords:
        if kw in html_lower:
            internal_hiring_signals.append(kw)
    detected["internal_tool_hiring_signals"] = internal_hiring_signals

    # --- Gap analysis ---

    if not monitoring:
        gaps.append({
            "gap": "No application monitoring or error tracking detected",
            "impact": "Bugs and outages go undetected until customers complain — no visibility into system health, error rates, or performance degradation",
            "opportunity": "Set up Sentry for error tracking and a monitoring stack (Datadog/New Relic) for uptime, performance, and alerting",
        })

    if not workflow:
        gaps.append({
            "gap": "No workflow automation or process integration tooling detected",
            "impact": "Business processes are likely manual or require staff to move data between systems by hand — hours of repetitive work that scales poorly",
            "opportunity": "Map and automate key internal workflows (lead routing, order processing, invoice generation, reporting) using custom automation or a workflow engine",
        })

    if not bi_tools:
        gaps.append({
            "gap": "No business intelligence or reporting platform detected",
            "impact": "Business decisions are made on gut feel or manually compiled spreadsheets — no real-time visibility into sales, operations, or customer data",
            "opportunity": "Build a custom internal dashboard or integrate a BI tool to centralise reporting across their key systems",
        })

    # SaaS potential — if they have API docs or multi-tenant signals
    if has_api_docs or has_multi_tenant:
        detected["saas_potential"] = True
        gaps.append({
            "gap": "Product shows SaaS or platform potential (API / multi-tenant signals detected)",
            "impact": "The existing product or process could be productised into a scalable SaaS offering but likely lacks the infrastructure (auth, billing, tenant isolation, onboarding flows) to do so",
            "opportunity": "Build out the SaaS layer — multi-tenant architecture, subscription billing, self-serve onboarding, admin dashboards, and usage analytics",
        })

    # Finance automation gap — has ecommerce/revenue but no finance tool visible
    if not finance_tools:
        gaps.append({
            "gap": "No finance or billing automation tools detected",
            "impact": "Invoicing, reconciliation, and financial reporting are likely done manually or in disconnected spreadsheets — error-prone and unscalable",
            "opportunity": "Integrate automated invoicing and financial reporting, or build a custom billing system connected to their existing stack",
        })

    return {
        "detected": detected,
        "gaps": gaps,
        "gap_count": len(gaps),
    }
