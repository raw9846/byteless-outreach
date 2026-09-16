from bs4 import BeautifulSoup
from typing import Dict, Any, List


# Tools grouped by function — detect what they're using
TOOL_CATEGORIES = {
    "ecommerce_platform": {
        "Shopify": ["cdn.shopify.com", "shopify.com"],
        "WooCommerce": ["woocommerce", "wc-ajax"],
        "Magento": ["mage/", "magento"],
        "BigCommerce": ["bigcommerce.com"],
        "Squarespace Commerce": ["squarespace.com"],
        "Wix Stores": ["wixstatic.com"],
        "PrestaShop": ["prestashop"],
        "OpenCart": ["opencart"],
    },
    "email_marketing": {
        "Klaviyo": ["klaviyo.com"],
        "Mailchimp": ["chimpstatic.com", "mailchimp"],
        "ActiveCampaign": ["activecampaign.com", "trackcmp.net"],
        "Drip": ["drip.com", "getdrip.com"],
        "Omnisend": ["omnisend.com"],
        "Sendgrid": ["sendgrid.com"],
        "ConvertKit": ["convertkit.com"],
        "Brevo": ["brevo.com", "sendinblue.com"],
    },
    "crm": {
        "HubSpot CRM": ["hs-scripts.com", "hubspot.com"],
        "Salesforce": ["salesforce.com", "sfdcstatic"],
        "Pipedrive": ["pipedrive.com"],
        "Zoho CRM": ["zoho.com"],
        "Monday CRM": ["monday.com"],
        "Freshsales": ["freshsales.io"],
    },
    "analytics": {
        "Google Analytics": ["google-analytics.com", "gtag("],
        "Google Tag Manager": ["googletagmanager.com"],
        "Hotjar": ["hotjar.com"],
        "Mixpanel": ["mixpanel.com"],
        "Heap": ["heap.io"],
        "Segment": ["segment.com", "segment.io"],
        "Amplitude": ["amplitude.com"],
        "Clarity": ["clarity.ms"],
        "FullStory": ["fullstory.com"],
    },
    "payment": {
        "Stripe": ["js.stripe.com"],
        "PayPal": ["paypal.com/sdk", "paypalobjects"],
        "Square": ["squareup.com"],
        "Braintree": ["braintreepayments.com"],
        "Klarna": ["klarna.com"],
        "Afterpay": ["afterpay.com"],
        "Affirm": ["affirm.com"],
    },
    "erp_inventory": {
        "NetSuite": ["netsuite.com"],
        "SAP": ["sap.com"],
        "Odoo": ["odoo.com"],
        "TradeGecko": ["tradegecko.com"],
        "Cin7": ["cin7.com"],
        "Brightpearl": ["brightpearl.com"],
        "Linnworks": ["linnworks.com"],
    },
    "shipping_fulfilment": {
        "ShipStation": ["shipstation.com"],
        "EasyPost": ["easypost.com"],
        "Shippo": ["goshippo.com"],
        "AfterShip": ["aftership.com"],
        "Narvar": ["narvar.com"],
    },
    "reviews_social_proof": {
        "Trustpilot": ["trustpilot.com"],
        "Yotpo": ["yotpo.com"],
        "Stamped.io": ["stamped.io"],
        "Judge.me": ["judge.me"],
        "Okendo": ["okendo.io"],
        "Reviews.io": ["reviews.io"],
        "Bazaarvoice": ["bazaarvoice.com"],
    },
    "a_b_testing": {
        "Optimizely": ["optimizely.com"],
        "Google Optimize": ["optimize.google.com"],
        "VWO": ["visualwebsiteoptimizer.com", "vwo.com"],
        "AB Tasty": ["abtasty.com"],
        "Convert": ["convert.com"],
    },
    "customer_success": {
        "Intercom": ["intercom.io"],
        "Drift": ["drift.com"],
        "Gorgias": ["gorgias.com"],
        "Zendesk": ["zendesk.com"],
        "Freshdesk": ["freshdesk.com"],
        "Help Scout": ["helpscout.com"],
    },
    "subscription": {
        "Recharge": ["rechargepayments.com"],
        "Bold Subscriptions": ["boldapps.net"],
        "Chargebee": ["chargebee.com"],
        "Recurly": ["recurly.com"],
        "Stripe Billing": ["js.stripe.com"],
    },
    "loyalty": {
        "Smile.io": ["smile.io"],
        "LoyaltyLion": ["loyaltylion.com"],
        "Yotpo Loyalty": ["yotpo.com"],
        "Stamped Loyalty": ["stamped.io"],
        "Marsello": ["marsello.com"],
    },
}

# Integration opportunities: if company has A but not B, that's a gap
INTEGRATION_RULES = [
    {
        "has": "ecommerce_platform",
        "missing": "crm",
        "gap": "E-commerce platform with no CRM integration",
        "impact": "Order data and customer data live in separate systems — no unified customer view, manual data reconciliation, missed upsell opportunities",
        "opportunity": "Build a CRM integration to sync orders, customer lifetime value, and segments automatically",
    },
    {
        "has": "ecommerce_platform",
        "missing": "email_marketing",
        "gap": "E-commerce store with no email marketing platform",
        "impact": "No automated abandoned cart recovery, post-purchase flows, or win-back campaigns — leaving significant repeat revenue on the table",
        "opportunity": "Integrate Klaviyo or similar with automated flows for cart recovery, post-purchase, and re-engagement",
    },
    {
        "has": "ecommerce_platform",
        "missing": "loyalty",
        "gap": "No loyalty or rewards program",
        "impact": "No incentive for repeat purchases — customer acquisition cost is never amortised across multiple orders",
        "opportunity": "Build or integrate a loyalty/rewards system to increase repeat purchase rate and LTV",
    },
    {
        "has": "ecommerce_platform",
        "missing": "reviews_social_proof",
        "gap": "No reviews or social proof system",
        "impact": "Product pages lack trust signals — conversion rates suffer especially for new visitors",
        "opportunity": "Integrate a reviews platform (Yotpo, Judge.me) with automated post-purchase review requests",
    },
    {
        "has": "ecommerce_platform",
        "missing": "subscription",
        "gap": "No subscription or recurring order capability",
        "impact": "Every purchase is a one-time transaction — no predictable recurring revenue from consumable or repeat-buy products",
        "opportunity": "Build subscription functionality for consumable products to generate predictable recurring revenue",
    },
    {
        "has": "ecommerce_platform",
        "missing": "erp_inventory",
        "gap": "E-commerce with no inventory management / ERP integration",
        "impact": "Inventory is managed manually or in a separate system — overselling, stockout surprises, and manual order reconciliation",
        "opportunity": "Integrate an inventory management system or build a custom sync between their store and fulfilment",
    },
    {
        "has": "crm",
        "missing": "email_marketing",
        "gap": "CRM with no email marketing automation",
        "impact": "Leads sit in the CRM with no automated nurturing — sales team has to manually follow up on every contact",
        "opportunity": "Build an automated email nurturing sequence triggered by CRM pipeline stages",
    },
    {
        "has": "analytics",
        "missing": "a_b_testing",
        "gap": "Analytics tracking but no A/B testing or conversion optimisation",
        "impact": "They can see traffic data but have no systematic way to improve conversion — leaving optimisation gains unmeasured",
        "opportunity": "Implement a CRO programme with A/B testing on key conversion pages",
    },
]


def detect_tool_stack(html: str) -> Dict[str, List[str]]:
    html_lower = html.lower()
    detected = {}
    for category, tools in TOOL_CATEGORIES.items():
        found = [
            tool for tool, patterns in tools.items()
            if any(p.lower() in html_lower for p in patterns)
        ]
        if found:
            detected[category] = found
    return detected


def find_integration_gaps(html: str) -> Dict[str, Any]:
    tool_stack = detect_tool_stack(html)
    gaps = []

    for rule in INTEGRATION_RULES:
        has_cat = rule["has"]
        missing_cat = rule["missing"]
        if has_cat in tool_stack and missing_cat not in tool_stack:
            gaps.append({
                "gap": rule["gap"],
                "has": tool_stack[has_cat],
                "missing_category": missing_cat,
                "impact": rule["impact"],
                "opportunity": rule["opportunity"],
            })

    # Tool sprawl — many disconnected tools
    total_tools = sum(len(v) for v in tool_stack.values())
    tool_sprawl = total_tools >= 5
    if tool_sprawl:
        tool_names = [t for tools in tool_stack.values() for t in tools]
        gaps.append({
            "gap": f"High tool sprawl — {total_tools} separate platforms detected",
            "has": tool_names,
            "impact": "Multiple disconnected SaaS tools mean data fragmentation, manual reconciliation between systems, and high subscription overhead",
            "opportunity": "Audit and consolidate the tool stack, or build a central integration layer / internal platform to unify data flows",
        })

    return {
        "tool_stack": tool_stack,
        "total_tools_detected": total_tools,
        "gaps": gaps,
        "gap_count": len(gaps),
    }
