import json
import subprocess
from typing import Dict, Any, Optional
from config import BYTELESS_CONTEXT
from ai.backend import run_prompt, get_backend

SYSTEM_PROMPT = f"""You are a senior technology and business systems consultant auditing companies for a software studio.
Your job is to find real, specific opportunities where custom software, automation, or systems work would create measurable business value.

About Byteless (the studio doing the outreach):
{BYTELESS_CONTEXT}

WHAT BYTELESS CAN BUILD — look for opportunities in ALL of these areas:

1. CUSTOMER-FACING WEB & APP DEVELOPMENT
   - Business running on Wix/Squarespace/basic CMS that needs a real custom web app
   - No customer portal or account area — everything done by email
   - No mobile app when one would clearly serve their customers
   - Legacy frontend (jQuery era) causing slow delivery and technical debt
   - Missing conversion infrastructure (no pricing page, no self-serve onboarding)

2. INTERNAL PROCESS AUTOMATION
   - Manual workflows that repeat daily/weekly (order processing, invoicing, reporting, approvals)
   - No workflow automation tools detected — staff moving data between systems by hand
   - No BI or reporting platform — decisions made on spreadsheets
   - No finance/billing automation — manual invoicing and reconciliation
   - Back-office processes that scale badly (works at 10 staff, breaks at 50)

3. SYSTEM INTEGRATIONS
   - Multiple disconnected SaaS tools with no data sync between them
   - Ecommerce platform with no CRM — customer data siloed
   - No email automation / abandoned cart recovery
   - Orders, inventory, and fulfilment in separate systems
   - CRM with no automated nurturing sequences

4. ECOMMERCE SPECIFIC
   - No loyalty or repeat-purchase incentive
   - No subscription/recurring revenue capability for consumable products
   - No reviews system — product pages lack social proof
   - Basic or no site search — poor product discovery on large catalogues
   - No post-purchase automation flows

5. SAAS / PLATFORM POTENTIAL
   - Company has a repeatable process or product that could be productised
   - API docs or developer signals detected — they may be building a platform without proper SaaS infrastructure
   - Multi-tenant signals without proper tenant architecture
   - Missing SaaS layer: subscription billing, self-serve onboarding, usage analytics, admin dashboards

6. DEVOPS & INFRASTRUCTURE
   - No error tracking or monitoring — outages discovered by customers
   - No observability into system health or performance
   - Old hosting infrastructure with no CDN — slow globally
   - Missing DevOps practices for a company that depends on its digital systems

Be honest — if a company's systems are genuinely solid, say so and set should_reach_out to false.
Only flag real issues grounded in the audit data. Never fabricate.
Frame everything as a business problem (lost revenue, operational cost, risk, scale ceiling) not a tech problem.

Respond with valid JSON only — no markdown, no explanation outside the JSON."""


def analyze_audit(lead_info: dict, audit_data: Dict[str, Any]) -> Optional[Dict]:
    # Build a focused summary of detected gaps to guide Claude
    gaps_summary = _extract_gaps_summary(audit_data)

    prompt = f"""{SYSTEM_PROMPT}

Analyze this audit for {lead_info.get("company_name", audit_data["domain"])}.

COMPANY PROFILE:
- Domain: {audit_data["domain"]}
- Industry: {lead_info.get("industry", "Unknown")}
- Size: {lead_info.get("employee_count", "Unknown")} employees
- Revenue: {lead_info.get("annual_revenue", "Unknown")}
- Contact: {lead_info.get("contact_name", "Unknown")}, {lead_info.get("contact_title", "")}

DETECTED GAPS (pre-analysed):
{gaps_summary}

FULL AUDIT DATA:
{json.dumps(audit_data, indent=2)}

Return this exact JSON structure:
{{
  "should_reach_out": true/false,
  "confidence": "high/medium/low",
  "company_summary": "1-2 sentence description of what this company does and how they operate",
  "findings": [
    {{
      "area": "area name — be specific: e.g. Internal Automation, SaaS Infrastructure, Ecommerce Integration, Custom Web App, DevOps",
      "issue": "specific concrete issue found, referencing actual detected data",
      "business_impact": "what this costs them commercially — lost revenue, staff hours, scale ceiling, or risk",
      "byteless_solution": "exactly what Byteless would build or implement to solve this"
    }}
  ],
  "top_finding": "single most impactful finding — one punchy sentence a founder would immediately relate to",
  "estimated_value": "rough sense of business value unlocked if solved (e.g. 'recovers 5-15% of abandoned revenue', 'saves ~10 staff hours/week')",
  "skip_reason": "if should_reach_out is false, explain specifically why — else null"
}}

Rules:
- Set should_reach_out to true only if there are 2+ genuine, specific, buildable opportunities
- Prioritise internal automation, integrations, and custom systems over surface-level SEO/design issues
- Each finding must be grounded in something the audit actually detected or conspicuously did NOT detect
- estimated_value should be honest and conservative — skip if you genuinely can't estimate"""

    try:
        result = run_prompt(prompt, timeout=120)

        text = result.stdout.strip()
        if not text:
            stderr = result.stderr.strip()
            return {"error": stderr or "Empty response", "should_reach_out": False, "skip_reason": "Analysis returned no output"}

        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

        return json.loads(text)

    except subprocess.TimeoutExpired:
        return {"error": "Timeout", "should_reach_out": False, "skip_reason": "Analysis timed out"}
    except json.JSONDecodeError:
        return {"error": "JSON parse failed", "raw": text, "should_reach_out": False, "skip_reason": "Analysis parse error"}
    except FileNotFoundError:
        return {"error": f"{get_backend()} CLI not found — ensure it's installed and in PATH", "should_reach_out": False, "skip_reason": f"{get_backend()} CLI missing"}
    except Exception as e:
        return {"error": str(e), "should_reach_out": False, "skip_reason": f"Analysis error: {e}"}


def _extract_gaps_summary(audit_data: dict) -> str:
    """Build a human-readable summary of all detected gaps to focus Claude's analysis."""
    lines = []

    for section_key, label in [
        ("automation", "Automation gaps"),
        ("integrations", "Integration gaps"),
        ("webapp", "Web/app gaps"),
        ("internal_systems", "Internal systems gaps"),
    ]:
        section = audit_data.get(section_key, {})
        gaps = section.get("gaps", [])
        if gaps:
            lines.append(f"\n{label} ({len(gaps)} found):")
            for g in gaps:
                lines.append(f"  - {g['gap']}: {g['impact']}")

    # Tool stack summary
    tool_stack = audit_data.get("integrations", {}).get("tool_stack", {})
    if tool_stack:
        tools = [t for tools in tool_stack.values() for t in tools]
        lines.append(f"\nDetected tools: {', '.join(tools)}")

    internal_detected = audit_data.get("internal_systems", {}).get("detected", {})
    if internal_detected.get("monitoring"):
        lines.append(f"Monitoring: {', '.join(internal_detected['monitoring'])}")
    elif internal_detected.get("monitoring") == []:
        lines.append("Monitoring: NONE detected")

    if internal_detected.get("workflow_automation"):
        lines.append(f"Workflow automation: {', '.join(internal_detected['workflow_automation'])}")
    elif internal_detected.get("workflow_automation") == []:
        lines.append("Workflow automation: NONE detected")

    if internal_detected.get("saas_potential"):
        lines.append("SaaS potential: API/multi-tenant signals detected")

    # Performance
    perf = audit_data.get("performance", {})
    mobile_scores = perf.get("mobile", {}).get("scores", perf.get("scores", {}))
    if mobile_scores.get("performance", 100) < 50:
        lines.append(f"Performance: critically slow (mobile score {mobile_scores.get('performance')})")
    elif mobile_scores.get("performance", 100) < 70:
        lines.append(f"Performance: poor (mobile score {mobile_scores.get('performance')})")

    # In-house engineering team (vs. just hiring signals)
    team = audit_data.get("team", {})
    if team.get("has_in_house_engineering_team"):
        lines.append(f"In-house engineering team: YES — titles found: {', '.join(team['engineering_titles_found'])}")
    elif team.get("team_page_found"):
        lines.append("In-house engineering team: team/about page found but no engineering titles listed")

    # Catalog depth
    catalog = audit_data.get("catalog", {})
    pj = catalog.get("products_json_page1_count")
    sm = catalog.get("product_sitemap_file_count")
    if pj is not None:
        lines.append(f"Catalog depth: {pj}+ products detected via products.json" + (" (capped at 250 — likely larger)" if pj == 250 else ""))
    if sm is not None:
        lines.append(f"Catalog depth: {sm} product-sitemap file(s) detected")

    return "\n".join(lines) if lines else "No pre-detected gaps — analyse the full audit data directly."
