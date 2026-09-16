from dataclasses import dataclass
from typing import Optional


@dataclass
class Lead:
    domain: str
    company_name: str
    contact_name: Optional[str] = None
    contact_title: Optional[str] = None
    contact_email: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[str] = None
    annual_revenue: Optional[str] = None
    linkedin_url: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
