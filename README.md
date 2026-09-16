# Byteless Outreach

A CLI tool that audits a company's public website and generates a personalised cold-outreach
email draft, flagging concrete automation/integration opportunities a software studio could pitch.

## What it does

For each company (given a domain, or a batch from a CSV):

1. **Technical audit** — scrapes the public site and runs:
   - Technology stack detection (CMS, analytics, CRM, payment, hosting, etc.)
   - PageSpeed Insights performance scoring (mobile + desktop)
   - SEO checks (title/meta/H1/schema/sitemap/robots)
   - HTTP security header analysis (HSTS, CSP, X-Frame-Options, etc.)
   - Automation, integration, internal-systems, and web-app gap detection
   - Job postings / hiring signals, social presence, review platform presence
2. **Firmographic + contact enrichment** — via the Apollo API (industry, size, revenue,
   funding, tech stack, and the most senior indexed contact for the domain)
3. **AI analysis** — the full audit is handed to an AI CLI (your choice — see below) to
   decide whether the company is worth reaching out to, and why
4. **Email draft generation** — a personalised cold email, grounded only in what was
   actually found (no fabricated claims)
5. *(optional)* **Google Sheets / Docs integration** — write results directly into a
   tracking spreadsheet or generate proposal documents

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env` with your **own** credentials (do not reuse anyone else's — see below):

- `PAGESPEED_API_KEY` — optional, raises your PageSpeed API quota
- `APOLLO_API_KEY` — optional, needed for firmographic/contact enrichment
  ([Apollo API docs](https://docs.apollo.io)) — scope the key to only the endpoints you need
  (`organizations/enrich`, `people/match`, `mixed_people/api_search`)
- `AI_BACKEND` — `claude` or `codex`, or leave unset to auto-detect whichever CLI you have
  installed. This tool works with either [Claude Code](https://claude.com/claude-code) or
  [OpenAI's Codex CLI](https://github.com/openai/codex) — install and log into whichever one
  you use
- `GOOGLE_SHEETS_CLIENT_ID` / `GOOGLE_SHEETS_CLIENT_SECRET` — only needed for the optional
  Sheets/Docs integration; requires setting up your own Google Cloud OAuth client (Desktop
  or Web application type) with the Sheets, Docs, and Drive APIs enabled

## Usage

```bash
# Single company
python3 main.py audit --domain acme.com --company "Acme Corp"

# Batch from an Apollo CSV export
python3 main.py batch --input leads.csv --limit 20

# Plain domain list (one per line, or "domain, Company Name")
python3 main.py from-list --input domains.txt

# Any CSV, mapping your own columns
python3 main.py from-csv --input export.csv --domain-col "Website" --company-col "Name"

# Review results
python3 main.py list
python3 main.py show --domain acme.com

# One-time auth for the optional Sheets/Docs integration
python3 main.py sheets-auth
```

Audit results, AI analysis, and email drafts are saved per-company under `companies/`, with
a running `tracker.csv` summary — both gitignored, since they'll contain your own prospect data.
