import csv
from pathlib import Path
from datetime import datetime
from config import TRACKER_FILE

COLUMNS = [
    "company", "domain", "contact_name", "contact_email", "industry",
    "should_reach_out", "confidence", "top_finding", "status", "date_audited",
]


class Tracker:
    def __init__(self):
        if not TRACKER_FILE.exists():
            with open(TRACKER_FILE, "w", newline="") as f:
                csv.DictWriter(f, fieldnames=COLUMNS).writeheader()

    def add(self, lead, analysis: dict):
        row = {
            "company": lead.company_name,
            "domain": lead.domain,
            "contact_name": lead.contact_name or "",
            "contact_email": lead.contact_email or "",
            "industry": lead.industry or "",
            "should_reach_out": analysis.get("should_reach_out", False),
            "confidence": analysis.get("confidence", ""),
            "top_finding": analysis.get("top_finding", ""),
            "status": "drafted" if analysis.get("should_reach_out") else "skipped",
            "date_audited": datetime.now().strftime("%Y-%m-%d"),
        }
        with open(TRACKER_FILE, "a", newline="") as f:
            csv.DictWriter(f, fieldnames=COLUMNS).writerow(row)

    def get_all(self) -> list:
        if not TRACKER_FILE.exists():
            return []
        with open(TRACKER_FILE, "r") as f:
            return list(csv.DictReader(f))

    def update_status(self, domain: str, status: str):
        rows = self.get_all()
        updated = False
        for row in rows:
            if row["domain"] == domain:
                row["status"] = status
                updated = True

        if updated:
            with open(TRACKER_FILE, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=COLUMNS)
                writer.writeheader()
                writer.writerows(rows)

        return updated
