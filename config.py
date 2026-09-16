import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PAGESPEED_API_KEY = os.getenv("PAGESPEED_API_KEY", "")
APOLLO_API_KEY = os.getenv("APOLLO_API_KEY", "")

OUTPUT_DIR = Path("companies")
TRACKER_FILE = Path("tracker.csv")

BYTELESS_CONTEXT = """
Byteless is a software studio that builds custom software solutions for businesses.
Services: web applications, mobile apps, business automation, system integrations,
technical consulting, and custom software architecture.
We identify inefficiencies in existing systems and build targeted solutions that save
time, reduce costs, and unlock growth for our clients.
"""
