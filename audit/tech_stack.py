from typing import Dict, List

SIGNATURES: Dict[str, Dict[str, List[str]]] = {
    "CMS": {
        "WordPress": ["wp-content/", "wp-includes/", "/wp-json/"],
        "Shopify": ["cdn.shopify.com", "shopify.theme"],
        "Wix": ["wixstatic.com", ".wix.com"],
        "Squarespace": ["squarespace.com", "squarespace-cdn"],
        "Webflow": ["webflow.com", "w-webflow-badge"],
        "Drupal": ["drupal.settings", "/sites/default/files"],
        "Joomla": ["/components/com_", "joomla"],
        "Ghost": ["ghost.io", "content/themes/"],
        "Contentful": ["contentful.com"],
        "Sanity": ["sanity.io"],
        "Prismic": ["prismic.io"],
        "Strapi": ["strapi.io"],
    },
    "Ecommerce Platform": {
        "WooCommerce": ["woocommerce", "wc-ajax", "wc_add_to_cart"],
        "Magento": ["mage/", "magento", "mageInit"],
        "BigCommerce": ["bigcommerce.com", "stencil"],
        "PrestaShop": ["prestashop", "addons.prestashop"],
        "OpenCart": ["opencart", "route=product"],
        "Shopware": ["shopware", "sw-plugin"],
        "Volusion": ["volusion.com"],
        "3dcart": ["3dcart.com"],
    },
    "Framework": {
        "React": ["react.production.min.js", "data-reactroot", "__react"],
        "Next.js": ["__next", "_next/static", "next/dist"],
        "Angular": ["ng-version", "ng-app", "angular.min.js"],
        "Vue.js": ["vue.min.js", "__vue__"],
        "Gatsby": ["gatsby-", "___gatsby"],
        "Nuxt.js": ["__nuxt", "_nuxt/"],
        "Svelte": ["svelte-", "__svelte"],
        "Remix": ["__remix_router"],
        "Astro": ["astro-island"],
        "SvelteKit": ["_app/immutable"],
    },
    "Analytics & Tracking": {
        "Google Analytics 4": ["gtag(", "ga4", "G-"],
        "Google Analytics UA": ["google-analytics.com/analytics.js", "UA-"],
        "Google Tag Manager": ["googletagmanager.com", "gtm.js"],
        "Hotjar": ["hotjar.com", "hj("],
        "Mixpanel": ["mixpanel.com"],
        "Heap": ["heap.io", "heap.load"],
        "Segment": ["segment.com/analytics.js", "cdn.segment.com"],
        "Amplitude": ["amplitude.com", "cdn.amplitude.com"],
        "Microsoft Clarity": ["clarity.ms"],
        "FullStory": ["fullstory.com", "fs.identify"],
        "Mouseflow": ["mouseflow.com"],
        "Lucky Orange": ["luckyorange.com"],
        "Crazy Egg": ["crazyegg.com"],
        "Pendo": ["pendo.io"],
    },
    "Marketing Automation & CRM": {
        "HubSpot": ["hs-scripts.com", "hubspot.com/hs-fs"],
        "Salesforce": ["salesforce.com", "sfdcstatic"],
        "Marketo": ["marketo.com", "munchkin.js"],
        "Pardot": ["pardot.com", "pi.pardot"],
        "ActiveCampaign": ["activecampaign.com", "trackcmp.net"],
        "Klaviyo": ["klaviyo.com"],
        "Mailchimp": ["chimpstatic.com", "mailchimp.com/subscribe"],
        "Drip": ["drip.com", "getdrip.com"],
        "ConvertKit": ["convertkit.com"],
        "Brevo": ["brevo.com", "sendinblue.com"],
        "Omnisend": ["omnisend.com"],
        "Zoho CRM": ["zoho.com/crm"],
        "Pipedrive": ["pipedrive.com"],
    },
    "Live Chat & Support": {
        "Intercom": ["intercom.io", "intercomcdn"],
        "Drift": ["drift.com", "js.driftt.com"],
        "Zendesk": ["zendesk.com", "zopim.com"],
        "Freshchat": ["freshchat.com", "wchat.freshchat"],
        "Tidio": ["tidio.com"],
        "Crisp": ["crisp.chat"],
        "LiveChat": ["livechatinc.com"],
        "Tawk.to": ["tawk.to"],
        "HubSpot Chat": ["hs-scripts.com"],
        "Gorgias": ["gorgias.com"],
        "Help Scout": ["helpscout.com", "helpscout.net"],
        "Olark": ["olark.com"],
    },
    "Payment": {
        "Stripe": ["js.stripe.com"],
        "PayPal": ["paypal.com/sdk", "paypalobjects.com"],
        "Square": ["squareup.com"],
        "Braintree": ["braintreepayments.com"],
        "Klarna": ["klarna.com"],
        "Afterpay": ["afterpay.com"],
        "Affirm": ["affirm.com"],
        "Sezzle": ["sezzle.com"],
        "Adyen": ["adyen.com"],
        "Checkout.com": ["checkout.com"],
    },
    "Booking & Scheduling": {
        "Calendly": ["calendly.com"],
        "Acuity": ["acuityscheduling.com"],
        "Cal.com": ["cal.com"],
        "Mindbody": ["mindbodyonline.com"],
        "Booksy": ["booksy.com"],
        "Setmore": ["setmore.com"],
        "SimplyBook": ["simplybook.me"],
        "HubSpot Meetings": ["hubspot.com/meetings"],
        "YouCanBook": ["youcanbook.me"],
    },
    "Hosting & CDN": {
        "Cloudflare": ["cloudflare", "__cf_bm"],
        "AWS CloudFront": ["cloudfront.net"],
        "AWS S3": ["amazonaws.com"],
        "Vercel": ["vercel.app", "_vercel"],
        "Netlify": ["netlify.com", "netlify.app"],
        "Fastly": ["fastly.net"],
        "Akamai": ["akamai.net", "akamaized.net"],
        "Bunny CDN": ["b-cdn.net"],
        "KeyCDN": ["kxcdn.com"],
    },
    "A/B Testing & CRO": {
        "Optimizely": ["optimizely.com"],
        "VWO": ["visualwebsiteoptimizer.com", "vwo.com"],
        "AB Tasty": ["abtasty.com"],
        "Convert": ["convert.com"],
        "Unbounce": ["unbounce.com"],
        "Google Optimize": ["optimize.google.com"],
    },
    "Loyalty & Retention": {
        "Smile.io": ["smile.io"],
        "LoyaltyLion": ["loyaltylion.com"],
        "Yotpo Loyalty": ["yotpo.com"],
        "Marsello": ["marsello.com"],
        "Stamped Loyalty": ["stamped.io"],
    },
    "Reviews & Social Proof": {
        "Trustpilot": ["trustpilot.com"],
        "Yotpo Reviews": ["yotpo.com"],
        "Judge.me": ["judge.me"],
        "Okendo": ["okendo.io"],
        "Stamped": ["stamped.io"],
        "Reviews.io": ["reviews.io"],
        "Bazaarvoice": ["bazaarvoice.com"],
        "PowerReviews": ["powerreviews.com"],
    },
    "Subscriptions": {
        "Recharge": ["rechargepayments.com"],
        "Bold Subscriptions": ["boldapps.net"],
        "Chargebee": ["chargebee.com"],
        "Recurly": ["recurly.com"],
        "Ordergroove": ["ordergroove.com"],
    },
    "Search": {
        "Algolia": ["algolia.com", "algolianet.com"],
        "Elasticsearch": ["elasticsearch"],
        "Typesense": ["typesense.org"],
        "Doofinder": ["doofinder.com"],
        "SearchPie": ["searchpie"],
        "Searchspring": ["searchspring.net"],
    },
    "ERP & Inventory": {
        "NetSuite": ["netsuite.com"],
        "SAP": ["sap.com"],
        "Odoo": ["odoo.com"],
        "Cin7": ["cin7.com"],
        "Brightpearl": ["brightpearl.com"],
        "Linnworks": ["linnworks.com"],
        "Skubana": ["skubana.com"],
        "Extensiv": ["extensiv.com"],
    },
    "Shipping & Fulfilment": {
        "ShipStation": ["shipstation.com"],
        "AfterShip": ["aftership.com"],
        "Narvar": ["narvar.com"],
        "Shippo": ["goshippo.com"],
        "EasyPost": ["easypost.com"],
        "ShipBob": ["shipbob.com"],
    },
}


def detect_tech_stack(html: str, headers: dict) -> Dict[str, List[str]]:
    html_lower = html.lower()
    detected = {}

    for category, techs in SIGNATURES.items():
        found = [
            tech for tech, patterns in techs.items()
            if any(p.lower() in html_lower for p in patterns)
        ]
        if found:
            detected[category] = found

    server = headers.get("Server") or headers.get("server", "")
    if server:
        detected["Server"] = [server]

    x_powered = headers.get("X-Powered-By") or headers.get("x-powered-by", "")
    if x_powered:
        detected["Runtime"] = [x_powered]

    return detected
