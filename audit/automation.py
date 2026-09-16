from bs4 import BeautifulSoup
from typing import Dict, Any


BOOKING_TOOLS = [
    "calendly.com", "acuityscheduling.com", "cal.com", "tidycal.com",
    "squareup.com/appointments", "mindbodyonline.com", "booksy.com",
    "setmore.com", "simplybook.me", "oncehub.com", "hubspot.com/meetings",
    "doodle.com", "youcanbook.me",
]

LIVE_CHAT_TOOLS = [
    "intercom.io", "intercomcdn", "drift.com", "zendesk.com", "zopim",
    "tidio.com", "crisp.chat", "livechat.com", "tawk.to", "freshchat",
    "hubspot.com/conversations", "chatra.io", "olark.com", "smartsupp.com",
    "userlike.com", "gorgias.com",
]

CHATBOT_TOOLS = [
    "landbot.io", "manychat.com", "chatfuel.com", "botpress", "voiceflow",
    "dialogflow", "collect.chat", "typeform.com",
]

HELPDESK_TOOLS = [
    "zendesk.com", "freshdesk.com", "helpscout.com", "intercom.io",
    "gorgias.com", "re:amaze", "reamaze.com", "kustomer.com",
]

QUOTE_CALCULATOR_SIGNALS = [
    "quote", "calculator", "estimate", "pricing-tool", "get-a-quote",
    "instant-quote", "price-calculator", "configurator",
]

CLIENT_PORTAL_SIGNALS = [
    "client portal", "client login", "customer portal", "customer login",
    "my account", "sign in", "log in", "member area", "dashboard",
    "portal.php", "client-area", "/portal", "/clients", "/customer",
    "login.php", "signin",
]

ORDER_TRACKING_SIGNALS = [
    "track order", "track my order", "order tracking", "track shipment",
    "where is my order", "order status",
]

LEAD_FORM_SIGNALS = [
    "contact us", "get in touch", "request a demo", "book a call",
    "schedule a call", "talk to sales", "get started",
]


def find_automation_gaps(html: str, domain: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")
    html_lower = html.lower()
    links_text = " ".join(a.get("href", "") + " " + (a.text or "") for a in soup.find_all("a")).lower()
    all_text = html_lower + " " + links_text

    gaps = []
    signals = {}

    # Booking / scheduling
    has_booking = any(tool in all_text for tool in BOOKING_TOOLS)
    signals["has_booking_tool"] = has_booking
    if not has_booking:
        gaps.append({
            "gap": "No online booking or scheduling system",
            "impact": "Customers can't self-serve appointments — every booking requires a phone call or email, adding friction and staff overhead",
            "opportunity": "Build or integrate an automated booking system with calendar sync, reminders, and confirmation emails",
        })

    # Live chat / support
    has_live_chat = any(tool in all_text for tool in LIVE_CHAT_TOOLS)
    has_chatbot = any(tool in all_text for tool in CHATBOT_TOOLS)
    signals["has_live_chat"] = has_live_chat
    signals["has_chatbot"] = has_chatbot
    if not has_live_chat and not has_chatbot:
        gaps.append({
            "gap": "No live chat or chatbot on site",
            "impact": "Visitors with questions leave instead of converting — lost leads that never make it to the contact form",
            "opportunity": "Integrate a chatbot for lead qualification and FAQ handling, or live chat for high-intent visitors",
        })

    # Client / customer portal
    has_portal = any(s in all_text for s in CLIENT_PORTAL_SIGNALS)
    signals["has_client_portal"] = has_portal
    if not has_portal:
        gaps.append({
            "gap": "No customer or client portal / login area",
            "impact": "Customers manage everything via email — no self-service for orders, documents, invoices, or account info",
            "opportunity": "Build a client portal for account management, order history, document sharing, or project status",
        })

    # Order tracking (relevant for ecommerce / logistics)
    has_order_tracking = any(s in all_text for s in ORDER_TRACKING_SIGNALS)
    signals["has_order_tracking"] = has_order_tracking

    # Quote / price calculator
    has_quote_tool = any(s in all_text for s in QUOTE_CALCULATOR_SIGNALS)
    signals["has_quote_tool"] = has_quote_tool
    if not has_quote_tool:
        gaps.append({
            "gap": "No online quote calculator or pricing tool",
            "impact": "Potential customers can't self-qualify on price — every enquiry requires manual back-and-forth before a number is given",
            "opportunity": "Build an interactive quote calculator or pricing configurator to pre-qualify leads and reduce sales overhead",
        })

    # Helpdesk
    has_helpdesk = any(tool in all_text for tool in HELPDESK_TOOLS)
    signals["has_helpdesk"] = has_helpdesk

    # Lead capture quality
    forms = soup.find_all("form")
    has_multi_field_form = any(len(f.find_all(["input", "select", "textarea"])) > 3 for f in forms)
    contact_only = not has_multi_field_form and not has_booking and not has_portal
    signals["contact_form_only"] = contact_only
    if contact_only:
        gaps.append({
            "gap": "Lead capture is a basic contact form only",
            "impact": "No qualification or nurturing — leads go cold waiting for a manual reply",
            "opportunity": "Build an automated lead qualification flow with instant response, segmentation, and CRM routing",
        })

    return {
        "signals": signals,
        "gaps": gaps,
        "gap_count": len(gaps),
    }
