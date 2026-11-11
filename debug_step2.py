
import sys
import os
import requests

# Add the cloned repo to path
sys.path.append("/tmp/ref_bot")

import one.config as config
from one.sheerid_verifier import SheerIDVerifier

def test():
    vid = "67c8c14f5f17a83b745e3f82"
    print(f"Testing Step 2 (Submit Info) for ID: {vid}")
    
    # Manually perform the POST request like the reference bot does
    headers = {
        "Content-Type": "application/json",
    }
    
    # We'll use the exact structure from the reference bot
    step2_body = {
        "firstName": "Test",
        "lastName": "User",
        "birthDate": "2000-01-01",
        "email": "test.user123@psu.edu",
        "phoneNumber": "",
        "organization": {
            "id": 2565,
            "idExtended": "2565",
            "name": "Pennsylvania State University-Main Campus",
        },
        "deviceFingerprintHash": "1234567890abcdef1234567890abcdef",
        "locale": "en-US",
        "metadata": {
            "marketConsentValue": False,
            "refererUrl": f"https://services.sheerid.com/verify/67c8c14f5f17a83b745e3f82/?verificationId={vid}",
            "verificationId": vid,
            "flags": '{"collect-info-step-email-first":"default","doc-upload-considerations":"default","doc-upload-may24":"default","doc-upload-redesign-use-legacy-message-keys":false,"docUpload-assertion-checklist":"default","font-size":"default","include-cvec-field-france-student":"not-labeled-optional"}',
            "submissionOptIn": "By submitting the personal information above, I acknowledge that my personal information is being collected under the privacy policy of the business from which I am seeking a discount",
        },
    }

    url = f"https://services.sheerid.com/rest/v2/verification/{vid}/step/collectStudentPersonalInfo"
    
    # Use proxy if configured
    import config as app_config
    proxies = {"http": app_config.PROXY_URL, "https": app_config.PROXY_URL} if app_config.USE_PROXY else None

    print(f"POST {url}")
    try:
        resp = requests.post(url, json=step2_body, headers=headers, proxies=proxies)
        print(f"Status: {resp.status_code}")
        print(f"Body: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
