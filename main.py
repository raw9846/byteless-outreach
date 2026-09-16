import sys
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from pathlib import Path

from leads.models import Lead
from leads.parser import parse_apollo_csv, parse_manual, parse_domain_list, parse_generic_csv
from audit.engine import run_audit
from ai.analyzer import analyze_audit
from ai.email_writer import write_email
from ai.backend import cli_installed, get_backend
from output.storage import save_output
from output.tracker import Tracker
from config import PAGESPEED_API_KEY, OUTPUT_DIR

console = Console()


def check_claude_cli():
    if not cli_installed():
        backend = get_backend()
        if backend == "codex":
            console.print("[red]Error: codex CLI not found. Install it (npm install -g @openai/codex) and run 'codex login' (or set CODEX_API_KEY).[/red]")
        else:
            console.print("[red]Error: claude CLI not found. Install Claude Code and run 'claude login'.[/red]")
        sys.exit(1)


def process_lead(lead: Lead, tracker: Tracker) -> bool:
    console.print(f"\n[bold cyan]→ {lead.company_name}[/bold cyan] ({lead.domain})")

    console.print("  [dim]Auditing public site...[/dim]")
    audit_data = run_audit(lead.domain, PAGESPEED_API_KEY, lead.company_name)

    if not audit_data.get("reachable"):
        console.print(f"  [yellow]⚠ Site unreachable (status {audit_data.get('status_code', 0)}), skipping[/yellow]")
        return False

    console.print("  [dim]Analysing with Claude...[/dim]")
    lead_dict = {
        "company_name": lead.company_name,
        "domain": lead.domain,
        "industry": lead.industry,
        "employee_count": lead.employee_count,
        "annual_revenue": lead.annual_revenue,
        "contact_name": lead.contact_name,
        "contact_title": lead.contact_title,
    }
    analysis = analyze_audit(lead_dict, audit_data)

    if not analysis.get("should_reach_out"):
        reason = analysis.get("skip_reason") or "No significant opportunities found"
        console.print(f"  [dim]⊘ Skip: {reason}[/dim]")
        tracker.add(lead, analysis)
        return False

    console.print("  [dim]Writing email draft...[/dim]")
    email = write_email(lead_dict, analysis)

    company_dir = save_output(lead.domain, lead.company_name, audit_data, analysis, email)
    tracker.add(lead, analysis)

    console.print(f"  [green]✓ Saved → {company_dir}[/green]")
    console.print(f"  [bold]Top finding:[/bold] {analysis.get('top_finding', '')}")
    return True


# ── CLI ──────────────────────────────────────────────────────────────────────

@click.group()
def cli():
    """Byteless outreach tool — audit companies, generate personalised email drafts."""
    pass


@cli.command()
@click.option("--domain", required=True, help="Company domain (e.g. acme.com)")
@click.option("--company", default=None, help="Company name")
@click.option("--contact", default=None, help="Contact full name")
@click.option("--title", default=None, help="Contact job title")
@click.option("--email", "contact_email", default=None, help="Contact email address")
@click.option("--industry", default=None, help="Industry")
def audit(domain, company, contact, title, contact_email, industry):
    """Audit a single company and generate an email draft."""
    check_claude_cli()
    tracker = Tracker()
    lead = parse_manual(domain, company, contact, title, contact_email, industry)
    process_lead(lead, tracker)


@cli.command()
@click.option("--input", "input_file", required=True, type=click.Path(exists=True), help="Apollo CSV export file")
@click.option("--limit", default=None, type=int, help="Max companies to process")
@click.option("--skip-existing/--no-skip-existing", default=True, help="Skip already-audited domains")
def batch(input_file, limit, skip_existing):
    """Process a batch of leads from an Apollo CSV export."""
    check_claude_cli()
    tracker = Tracker()

    leads = parse_apollo_csv(input_file)
    console.print(f"[bold]Loaded {len(leads)} leads from {input_file}[/bold]")

    if skip_existing:
        existing = {row["domain"] for row in tracker.get_all()}
        leads = [l for l in leads if l.domain not in existing]
        console.print(f"[dim]{len(leads)} new leads after skipping already-audited[/dim]")

    if limit:
        leads = leads[:limit]

    drafted, skipped = 0, 0
    for lead in leads:
        result = process_lead(lead, tracker)
        if result:
            drafted += 1
        else:
            skipped += 1

    console.print(f"\n[bold green]Done.[/bold green] {drafted} email drafts created, {skipped} skipped.")


def _run_batch(leads, label):
    tracker = Tracker()
    if not leads:
        console.print("[yellow]No leads found.[/yellow]")
        return
    existing = {row["domain"] for row in tracker.get_all()}
    new_leads = [l for l in leads if l.domain not in existing]
    console.print(f"[bold]Loaded {len(leads)} leads from {label}[/bold]")
    console.print(f"[dim]{len(new_leads)} new after skipping already-audited[/dim]")
    drafted, skipped = 0, 0
    for lead in new_leads:
        if process_lead(lead, tracker):
            drafted += 1
        else:
            skipped += 1
    console.print(f"\n[bold green]Done.[/bold green] {drafted} drafts created, {skipped} skipped.")


@cli.command()
@click.option("--input", "input_file", required=True, type=click.Path(exists=True), help="Plain text file — one domain per line")
@click.option("--industry", default=None, help="Industry label to apply to all leads")
def from_list(input_file, industry):
    """Audit companies from a plain text file (one domain per line).

    Each line can be just a domain, or 'domain, Company Name'.
    Lines starting with # are ignored.

    \b
    Example file:
        acme.com, Acme Corp
        globex.com
        # this line is ignored
    """
    check_claude_cli()
    leads = parse_domain_list(input_file, industry=industry)
    _run_batch(leads, input_file)


@cli.command()
@click.option("--input", "input_file", required=True, type=click.Path(exists=True), help="Any CSV file")
@click.option("--domain-col", required=True, help="Column name containing the domain/website")
@click.option("--company-col", default=None, help="Column name for company name")
@click.option("--contact-col", default=None, help="Column name for contact full name")
@click.option("--title-col", default=None, help="Column name for contact job title")
@click.option("--email-col", default=None, help="Column name for contact email")
@click.option("--industry-col", default=None, help="Column name for industry")
def from_csv(input_file, domain_col, company_col, contact_col, title_col, email_col, industry_col):
    """Audit companies from any CSV — you map which columns to use.

    \b
    Example (Crunchbase export):
        python3 main.py from-csv --input crunchbase.csv --domain-col "Website" --company-col "Organization Name" --industry-col "Industries"

    \b
    Example (Hunter.io export):
        python3 main.py from-csv --input hunter.csv --domain-col "domain" --contact-col "full_name" --email-col "email"
    """
    check_claude_cli()
    leads = parse_generic_csv(
        input_file,
        domain_col=domain_col,
        company_col=company_col,
        contact_col=contact_col,
        title_col=title_col,
        email_col=email_col,
        industry_col=industry_col,
    )
    _run_batch(leads, input_file)


@cli.command()
@click.option("--domain", required=True, help="Company domain to display")
def show(domain):
    """Show the audit report and email draft for a company."""
    import json

    OUTPUT_DIR.mkdir(exist_ok=True)
    company_dir = None
    for d in OUTPUT_DIR.iterdir():
        if d.is_dir():
            raw = d / "audit_raw.json"
            if raw.exists():
                with open(raw) as f:
                    data = json.load(f)
                if data.get("domain") == domain:
                    company_dir = d
                    break

    if not company_dir:
        console.print(f"[red]No audit found for {domain}[/red]")
        return

    audit_file = company_dir / "audit.md"
    if audit_file.exists():
        console.print(Panel(audit_file.read_text(), title="Audit Report", border_style="cyan"))

    email_file = company_dir / "email_draft.txt"
    if email_file.exists():
        console.print(Panel(email_file.read_text(), title="Email Draft — ready to copy", border_style="green"))


@cli.command("list")
@click.option("--status", default=None, help="Filter: drafted / skipped / sent / replied / booked")
def list_companies(status):
    """List all audited companies with their status."""
    tracker = Tracker()
    rows = tracker.get_all()

    if status:
        rows = [r for r in rows if r["status"] == status]

    table = Table(title=f"Byteless Outreach Tracker ({len(rows)} companies)")
    table.add_column("Company", style="bold", min_width=20)
    table.add_column("Domain", min_width=18)
    table.add_column("Contact")
    table.add_column("Reach Out?", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Top Finding", max_width=50)

    for row in rows:
        reach = row.get("should_reach_out", "")
        is_yes = str(reach).lower() in ("true", "1", "yes")
        table.add_row(
            row["company"],
            row["domain"],
            row.get("contact_name", "") or "-",
            Text("YES", style="green bold") if is_yes else Text("no", style="dim"),
            row.get("status", ""),
            (row.get("top_finding") or "")[:50],
        )

    console.print(table)


@cli.command()
@click.option("--domain", required=True, help="Company domain to update")
@click.option("--status", required=True,
              type=click.Choice(["drafted", "sent", "replied", "booked", "closed", "not-interested"]))
def update(domain, status):
    """Update the pipeline status of a company (after you send an email, get a reply, etc.)."""
    tracker = Tracker()
    if tracker.update_status(domain, status):
        console.print(f"[green]Updated {domain} → {status}[/green]")
    else:
        console.print(f"[yellow]No entry found for {domain}[/yellow]")


@cli.command("sheets-auth")
def sheets_auth():
    """One-time interactive OAuth login for direct Google Sheets/Docs/Drive API access.

    Opens a browser for consent, then caches a refresh token locally so
    future runs don't need to re-authorize. Covers Sheets, Docs, and Drive
    (file-create) scopes in one flow.
    """
    from sheets.auth import get_credentials
    get_credentials()
    console.print("[green]Google Sheets/Docs/Drive access authorized and cached.[/green]")


if __name__ == "__main__":
    cli()
