import subprocess
from typing import Dict, Any
from config import BYTELESS_CONTEXT
from ai.backend import run_prompt, get_backend

EMAIL_SYSTEM = f"""You write cold outreach emails for Byteless, a software studio.

Rules:
- Feel personal and researched, never like a template
- Reference their specific business and findings by name
- Be direct and concise — no corporate speak, no buzzwords
- The goal is ONE thing: get a 15-minute call
- Total email body: 120-180 words max
- Tone: like a smart peer who noticed something, not a vendor pitching

About Byteless:
{BYTELESS_CONTEXT}"""


def write_email(lead_info: dict, analysis: Dict[str, Any]) -> str:
    contact = lead_info.get("contact_name") or "there"
    first_name = contact.split()[0] if contact != "there" else "there"
    findings_text = "\n".join(
        f"- {f['area']}: {f['issue']} → {f['business_impact']}"
        for f in analysis.get("findings", [])
    )

    prompt = f"""{EMAIL_SYSTEM}

Write a cold outreach email from Byteless to {first_name} at {lead_info.get("company_name", "")}.

RECIPIENT: {contact}, {lead_info.get("contact_title", "")}
COMPANY: {lead_info.get("company_name", "")} ({lead_info.get("domain", "")})
WHAT THEY DO: {analysis.get("company_summary", "")}

TOP FINDING: {analysis.get("top_finding", "")}

ALL FINDINGS:
{findings_text}

EMAIL STRUCTURE:
Subject: [specific, not clickbait, references their situation]

[Opening: 1-2 sentences that show you actually looked at their business — mention something specific]

[Body: Reference 1-2 findings naturally, framed as business problems not tech problems.
Don't say "your tech stack" or "we noticed your website". Say what it costs them.]

[Offer: 1 sentence — free product roadmap/architecture consult, no obligation]

[CTA: reply or book a 15-min call — keep it soft, not pushy]

[Sign-off]
[YOUR NAME]
Byteless

Format the output as:
Subject: [subject line]

[email body]"""

    try:
        result = run_prompt(prompt, timeout=120)

        text = result.stdout.strip()
        if not text:
            stderr = result.stderr.strip()
            return f"Error generating email: {stderr or 'Empty response'}"
        return text

    except subprocess.TimeoutExpired:
        return "Error generating email: timed out"
    except FileNotFoundError:
        return f"Error: {get_backend()} CLI not found — ensure it's installed and in PATH"
    except Exception as e:
        return f"Error generating email: {e}"
