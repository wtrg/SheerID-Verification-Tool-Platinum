
import requests
import json
import config

# The suspected Program ID provided by user
PROGRAM_ID = "67c8c14f5f17a83b745e3f82"
BASE_URL = "https://services.sheerid.com/rest/v2"

def test_init_session():
    print(f"Testing Session Creation for Program ID: {PROGRAM_ID}")
    
    proxies = None
    if config.USE_PROXY:
        proxies = {"http": config.PROXY_URL, "https": config.PROXY_URL}
        print(f"Using Proxy: {config.PROXY_URL}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    url = f"{BASE_URL}/verification/program/{PROGRAM_ID}"
    
    try:
        print(f"POST {url}")
        resp = requests.post(url, headers=headers, proxies=proxies, timeout=10)
        
        print(f"Status Code: {resp.status_code}")
        print(f"Response: {resp.text}")
        
        if resp.status_code == 200 or resp.status_code == 201:
            data = resp.json()
            vid = data.get("verificationId")
            if vid:
                print(f"\n✅ SUCCESS! Created NEW Verification ID: {vid}")
                print("This proves the Program ID is valid and we can generate unlimited sessions.")
            else:
                print("\n❌ Failed to get verificationId from response.")
        elif resp.status_code == 404:
            print("\n❌ 404 Not Found. This means the ID is NOT a Program ID, or the API endpoint is wrong.")
            print("Trying to treat it as a Verification ID...")
            
            # Check if it's an existing verif ID
            check_url = f"{BASE_URL}/verification/{PROGRAM_ID}"
            resp2 = requests.get(check_url, headers=headers, proxies=proxies)
            print(f"GET {check_url} -> {resp2.status_code}")
            print(resp2.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_init_session()
