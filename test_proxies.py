import os
import requests
import concurrent.futures
from dotenv import load_dotenv

load_dotenv()

proxies_list = [
    "198.23.239.134:6540",
    "107.172.163.27:6543",
    "216.10.27.159:6837",
    "23.26.71.145:5628",
    "23.229.19.94:8689",
    "2.57.20.2:5994"
]

auth = os.getenv("PROXY_AUTH", "user:pass")

def check_proxy(proxy_endpoint):
    proxy_url = f"http://{auth}@{proxy_endpoint}"
    proxies = {"http": proxy_url, "https": proxy_url}
    
    try:
        resp = requests.get("http://ip-api.com/json/?fields=status,message,country,isp,org,as,mobile,proxy,hosting,query", proxies=proxies, timeout=5)
        data = resp.json()
        
        if data['status'] == 'success':
            return {
                "ip": data['query'],
                "country": data['country'],
                "isp": data['isp'],
                "hosting": data['hosting'],
                "endpoint": proxy_endpoint,
                "score": calculate_score(data)
            }
    except:
        pass
    return None

def calculate_score(data):
    score = 0
    if data['country'] == 'United States': score += 20
    if not data['hosting']: score += 50
    if not data['proxy']: score += 10
    
    bad_isps = ['ColoCrossing', 'RackNerd', 'DigitalOcean', 'Choopa', 'Datacenter', 'Host', 'Cloud']
    if any(b.lower() in data['isp'].lower() for b in bad_isps):
        score -= 30
        
    good_isps = ['Comcast', 'AT&T', 'Verizon', 'Charter', 'Spectrum']
    if any(g.lower() in data['isp'].lower() for g in good_isps):
        score += 50
        
    return score

print("Checking 6 proxies from your list...")
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(check_proxy, proxies_list))

best_proxy = None
max_score = -100

for res in results:
    if res:
        status = "✅ RESI" if not res['hosting'] else "❌ DC"
        print(f"[{status}] {res['ip']} | ISP: {res['isp']} | Score: {res['score']}")
        if res['score'] > max_score:
            max_score = res['score']
            best_proxy = res

if best_proxy:
    print(f"\n🏆 Best Proxy: {best_proxy['endpoint']} ({best_proxy['isp']})")
    
    # Update config.py automatically
    import config
    
    # Read original file
    with open('config.py', 'r') as f:
        lines = f.readlines()
        
    # Rewrite with new proxy
    with open('config.py', 'w') as f:
        for line in lines:
            if "USE_PROXY =" in line:
                f.write("USE_PROXY = True\n")
            elif "PROXY_URL =" in line:
                f.write(f'PROXY_URL = "http://{auth}@{best_proxy["endpoint"]}"\n')
            else:
                f.write(line)
    
    print("✅ updated config.py with this proxy!")
else:
    print("\n❌ All proxies failed or are poor quality.")
