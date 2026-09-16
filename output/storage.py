import json
from pathlib import Path
from datetime import datetime
from config import OUTPUT_DIR


def _safe_name(name: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name.lower()).strip("_")


def save_output(domain: str, company_name: str, audit_data: dict, analysis: dict, email: str) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    company_dir = OUTPUT_DIR / _safe_name(company_name or domain)
    company_dir.mkdir(parents=True, exist_ok=True)

    with open(company_dir / "audit_raw.json", "w") as f:
        json.dump(audit_data, f, indent=2)

    with open(company_dir / "analysis.json", "w") as f:
        json.dump(analysis, f, indent=2)

    audit_md = _format_audit_report(domain, company_name, audit_data, analysis)
    (company_dir / "audit.md").write_text(audit_md)

    (company_dir / "email_draft.txt").write_text(email)

    return company_dir


def _format_audit_report(domain, company_name, audit, analysis) -> str:
    reach = "YES" if analysis.get("should_reach_out") else "NO"
    conf = analysis.get("confidence", "")
    lines = [
        f"# Audit: {company_name}",
        f"**Domain:** {domain}  |  **Date:** {datetime.now().strftime('%Y-%m-%d')}  |  **Reach Out:** {reach} ({conf})",
        "",
        "## Company Summary",
        analysis.get("company_summary", "N/A"),
        "",
        "## Findings",
    ]

    for f in analysis.get("findings", []):
        lines += [
            f"### {f.get('area', '')}",
            f"**Issue:** {f.get('issue', '')}",
            f"**Business Impact:** {f.get('business_impact', '')}",
            f"**Byteless Solution:** {f.get('byteless_solution', '')}",
            "",
        ]

    if analysis.get("skip_reason"):
        lines += ["## Skip Reason", analysis["skip_reason"], ""]

    lines += ["## Tech Stack", ""]
    for cat, items in audit.get("tech_stack", {}).items():
        lines.append(f"- **{cat}:** {', '.join(items)}")

    # Internal systems gaps
    internal = audit.get("internal_systems", {})
    if internal.get("gaps"):
        lines += ["", "## Internal Systems & Process Automation Gaps", ""]
        for g in internal["gaps"]:
            lines += [f"### {g['gap']}", f"**Impact:** {g['impact']}", f"**Opportunity:** {g['opportunity']}", ""]
        det = internal.get("detected", {})
        if det.get("monitoring"):
            lines.append(f"- Monitoring detected: {', '.join(det['monitoring'])}")
        if det.get("workflow_automation"):
            lines.append(f"- Workflow tools detected: {', '.join(det['workflow_automation'])}")
        if det.get("saas_potential"):
            lines.append("- SaaS/platform potential signals detected")

    # Automation gaps
    auto = audit.get("automation", {})
    if auto.get("gaps"):
        lines += ["", "## Automation Gaps", ""]
        for g in auto["gaps"]:
            lines += [f"### {g['gap']}", f"**Impact:** {g['impact']}", f"**Opportunity:** {g['opportunity']}", ""]

    # Integration gaps
    integr = audit.get("integrations", {})
    if integr.get("gaps"):
        lines += ["", "## Integration Gaps", ""]
        for g in integr["gaps"]:
            lines += [f"### {g['gap']}", f"**Impact:** {g['impact']}", f"**Opportunity:** {g['opportunity']}", ""]

    # Web/app signals
    webapp = audit.get("webapp", {})
    if webapp.get("gaps"):
        lines += ["", "## Web / App Development Gaps", ""]
        for g in webapp["gaps"]:
            lines += [f"### {g['gap']}", f"**Impact:** {g['impact']}", f"**Opportunity:** {g['opportunity']}", ""]

    # Performance
    perf = audit.get("performance", {})
    lines += ["", "## Performance Scores", ""]
    mobile_scores = perf.get("mobile", {}).get("scores", perf.get("scores", {}))
    desktop_scores = perf.get("desktop", {}).get("scores", {})
    for metric, score in mobile_scores.items():
        desktop = desktop_scores.get(metric, "")
        desktop_str = f" | desktop: {desktop}" if desktop else ""
        lines.append(f"- {metric}: {score}/100 (mobile){desktop_str}")
    if perf.get("opportunities"):
        lines += ["", "**Specific Issues:**"]
        for opp in perf["opportunities"][:6]:
            saving = f" (~{opp['potential_saving_ms']}ms)" if opp.get("potential_saving_ms") else ""
            lines.append(f"- {opp['issue']}{saving}")

    # Tech stack
    lines += ["", "## Tech Stack", ""]
    for cat, items in audit.get("tech_stack", {}).items():
        lines.append(f"- **{cat}:** {', '.join(items)}")

    # Detected tools from integrations module
    tool_stack = integr.get("tool_stack", {})
    if tool_stack:
        lines += ["", "## Detected Tools", ""]
        for cat, tools in tool_stack.items():
            lines.append(f"- **{cat.replace('_', ' ').title()}:** {', '.join(tools)}")

    lines += ["", "## SEO Issues", ""]
    for issue in audit.get("seo", {}).get("issues", []):
        lines.append(f"- {issue}")

    lines += ["", "## Social Presence", ""]
    social = audit.get("social", {})
    for platform, present in social.get("platforms", {}).items():
        status = "✓" if present else "✗"
        lines.append(f"- {status} {platform}")

    return "\n".join(lines)
