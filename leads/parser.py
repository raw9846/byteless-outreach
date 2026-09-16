import pandas as pd
from typing import List
from .models import Lead


def clean_domain(raw: str) -> str:
    if not raw or str(raw) == "nan":
        return ""
    raw = str(raw).strip().lower()
    raw = raw.replace("https://", "").replace("http://", "").replace("www.", "")
    raw = raw.split("/")[0]
    return raw.strip()


def parse_apollo_csv(file_path: str) -> List[Lead]:
    df = pd.read_csv(file_path)
    leads = []

    for _, row in df.iterrows():
        domain = clean_domain(row.get("Company Website", ""))
        if not domain:
            continue

        first = str(row.get("First Name", "") or "").strip()
        last = str(row.get("Last Name", "") or "").strip()
        contact_name = f"{first} {last}".strip() or None

        def safe(col):
            val = row.get(col, "")
            return str(val).strip() if val and str(val) != "nan" else None

        lead = Lead(
            domain=domain,
            company_name=safe("Company") or domain,
            contact_name=contact_name,
            contact_title=safe("Title"),
            contact_email=safe("Email"),
            industry=safe("Industry"),
            employee_count=safe("# Employees"),
            annual_revenue=safe("Annual Revenue"),
            linkedin_url=safe("Linkedin Url"),
            city=safe("City"),
            country=safe("Country"),
        )
        leads.append(lead)

    return leads


def parse_manual(domain: str, company: str = None, contact: str = None,
                 title: str = None, email: str = None, industry: str = None) -> Lead:
    return Lead(
        domain=clean_domain(domain),
        company_name=company or domain,
        contact_name=contact,
        contact_title=title,
        contact_email=email,
        industry=industry,
    )


def parse_domain_list(file_path: str, industry: str = None) -> List[Lead]:
    """Plain text file — one domain (or 'domain, Company Name') per line."""
    leads = []
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split(",", 1)]
            domain = clean_domain(parts[0])
            if not domain:
                continue
            company = parts[1] if len(parts) > 1 else domain
            leads.append(Lead(
                domain=domain,
                company_name=company,
                industry=industry,
            ))
    return leads


def parse_generic_csv(file_path: str, domain_col: str, company_col: str = None,
                      contact_col: str = None, title_col: str = None,
                      email_col: str = None, industry_col: str = None) -> List[Lead]:
    """Any CSV — you specify which columns map to what."""
    df = pd.read_csv(file_path)
    leads = []

    def safe(row, col):
        if not col:
            return None
        val = row.get(col, "")
        return str(val).strip() if val and str(val) != "nan" else None

    for _, row in df.iterrows():
        domain = clean_domain(row.get(domain_col, ""))
        if not domain:
            continue
        leads.append(Lead(
            domain=domain,
            company_name=safe(row, company_col) or domain,
            contact_name=safe(row, contact_col),
            contact_title=safe(row, title_col),
            contact_email=safe(row, email_col),
            industry=safe(row, industry_col),
        ))
    return leads
