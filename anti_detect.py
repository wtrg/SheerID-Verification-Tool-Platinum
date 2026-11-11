"""
Anti-Detection Module for SheerID Verification Tools
Shared module for better anti-fraud bypass & Cloudflare Turnstile mitigation

Features:
- Consistent Chrome 131 fingerprinting & matching Sec-CH-UA client hints
- Browser-grade header ordering and NewRelic tracing
- Request delay randomization
- TLS fingerprint spoofing with Chrome impersonation (curl_cffi)
- Session pre-warming for Cloudflare cookie initialization
"""

import random
import hashlib
import time
import uuid
import base64
import json
import sys

# ============ CHROME IMPERSONATION VERSIONS ============
DEFAULT_IMPERSONATE = "chrome131"

UA_PROFILES = [
    {
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "platform": '"Windows"',
        "sec_ch_ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "mobile": "?0"
    },
    {
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "platform": '"Windows"',
        "sec_ch_ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        "mobile": "?0"
    }
]

def get_random_profile():
    return random.choice(UA_PROFILES)

def get_random_user_agent():
    return UA_PROFILES[0]["ua"]

def get_fingerprint():
    return hashlib.md5(f"{time.time()}_{random.random()}".encode()).hexdigest()

def generate_newrelic_headers():
    trace_id = uuid.uuid4().hex[:32]
    span_id = uuid.uuid4().hex[:16]
    timestamp = int(time.time() * 1000)
    payload = {
        "v": [0, 1],
        "d": {
            "ty": "Browser",
            "ac": "364029",
            "ap": "120719994",
            "id": span_id,
            "tr": trace_id,
            "ti": timestamp
        }
    }
    return {
        "newrelic": base64.b64encode(json.dumps(payload).encode()).decode(),
        "traceparent": f"00-{trace_id}-{span_id}-01",
        "tracestate": f"364029@nr=0-1-364029-120719994-{span_id}----{timestamp}",
    }

def get_headers(for_sheerid=True, profile=None):
    prof = profile or UA_PROFILES[0]
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "sec-ch-ua": prof["sec_ch_ua"],
        "sec-ch-ua-mobile": prof["mobile"],
        "sec-ch-ua-platform": prof["platform"],
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": prof["ua"],
    }
    if for_sheerid:
        headers.update({
            "clientversion": "2.193.0",
            "clientname": "jslib",
            "x-sheerid-target-platform": "web",
            **generate_newrelic_headers()
        })
    return headers

def random_delay(min_ms=300, max_ms=1200):
    time.sleep(random.randint(min_ms, max_ms) / 1000)

def create_session(proxy=None, impersonate=None):
    from curl_cffi import requests as curl_requests
    imp = impersonate or DEFAULT_IMPERSONATE
    proxies = {"http": proxy, "https": proxy} if proxy else None
    session = curl_requests.Session(proxies=proxies, impersonate=imp)
    # Store consistent profile in session
    session.profile = get_random_profile()
    return session, "curl_cffi", imp

def warm_session(session, program_id=None, verification_id=None):
    """Warm up session with SheerID endpoints to collect cookies & lower Turnstile risk score"""
    prof = getattr(session, "profile", UA_PROFILES[0])
    try:
        session.get("https://services.sheerid.com/rest/v2/config", headers=get_headers(profile=prof))
        if program_id and verification_id:
            landing = f"https://services.sheerid.com/verify/{program_id}/?verificationId={verification_id}"
            headers = get_headers(for_sheerid=False, profile=prof)
            headers["accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            session.get(landing, headers=headers)
    except Exception as e:
        print(f"[!] Session warming note: {e}")
    return session

def handle_fraud_rejection(retry_count, error_payload, message=""):
    print(f"🚨 FRAUD REJECTION: {message}")
