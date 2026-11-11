
import requests
import json
import config

PROGRAM_ID = "67c8c14f5f17a83b745e3f82"

endpoints = [
    f"https://services.sheerid.com/rest/v2/verification/program/{PROGRAM_ID}",
    f"https://services.sheerid.com/rest/v2/info",
    f"https://services.sheerid.com/rest/v2/verification",
    f"https://services.sheerid.com/rest/v2/program/{PROGRAM_ID}/verification"
]

def brute_init():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "clientversion": "2.193.0"
    }
    
    proxies = {"http": config.PROXY_URL, "https": config.PROXY_URL} if config.USE_PROXY else None

    for url in endpoints:
        print(f"--- Testing: {url} ---")
        try:
            # Try POST with ID in body
            resp = requests.post(url, json={"programId": PROGRAM_ID}, headers=headers, proxies=proxies, timeout=5)
            print(f"POST result: {resp.status_code}")
            if resp.status_code == 200:
                print(resp.text)
                return
            
            # Try GET
            resp = requests.get(url, headers=headers, proxies=proxies, timeout=5)
            print(f"GET result: {resp.status_code}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    brute_init()
