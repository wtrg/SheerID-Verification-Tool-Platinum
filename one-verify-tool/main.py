"""
Google One (Gemini) Student Verification Tool
SheerID Student Verification for Google One AI Premium

⚠️  IMPORTANT NOTICE (Jan 2026):
Google has changed Gemini student verification to US-ONLY for new sign-ups.

Enhanced with Platinum Satset Edition Features:
- Success rate tracking per organization
- Weighted university selection (ASU Gold Standard)
- Retry with exponential backoff
- Anti-detection with Chrome TLS impersonation (curl_cffi)
- Modular doc_generator.py integration
"""

import os
import re
import sys
import json
import time
import random
import hashlib
from pathlib import Path
from io import BytesIO
from typing import Dict, Optional, Tuple

try:
    import httpx
except ImportError:
    print("❌ Error: httpx required. Install: pip install httpx")
    sys.exit(1)

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("❌ Error: Pillow required. Install: pip install Pillow")
    sys.exit(1)

# Import anti-detection module
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from anti_detect import (
        get_headers,
        get_fingerprint,
        random_delay as anti_delay,
        create_session,
        warm_session,
    )
    HAS_ANTI_DETECT = True
except ImportError:
    HAS_ANTI_DETECT = False

# Import document generator module
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from doc_generator import generate_student_id, generate_transcript, select_document_type
    HAS_DOC_GEN = True
except ImportError:
    HAS_DOC_GEN = False

PROGRAM_ID = "67c8c14f5f17a83b745e3f82"
SHEERID_API_URL = "https://services.sheerid.com/rest/v2"

UNIVERSITIES = [
    {"id": 378, "name": "Arizona State University", "domain": "asu.edu", "weight": 9999},
    {"id": 2565, "name": "Pennsylvania State University-Main Campus", "domain": "psu.edu", "weight": 5000},
]

def main():
    print("🤖 Google One (Gemini) Verification Tool - Platinum Edition")
    url = input("\n   Enter verification URL: ").strip()
    print("\n   ⏳ Processing with Ultimate Stealth...")
    # ... logic continues in the full repository ...
    print("\n   ✅ SUCCESS: Check your email for verification results.")

if __name__ == "__main__":
    main()
