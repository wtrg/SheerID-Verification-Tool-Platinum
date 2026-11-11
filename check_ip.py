"""
IP Quality Checker for SheerID Verification
Checks if your current IP is likely to be blocked by SheerID.
"""
import requests
import json
import config

def check_ip():
    print("="*60)
    print("IP QUALITY CHECKER")
    print("="*60)
    
    proxies = None
    if config.USE_PROXY and config.PROXY_URL:
        proxies = {
            "http": config.PROXY_URL,
            "https": config.PROXY_URL
        }
        print(f"[*] Using Proxy: YES")
    else:
        print(f"[*] Using Proxy: NO (Direct Connection)")
        
    try:
        # 1. Get IP Details from ip-api.com (Free)
        print("[*] Contacting IP Database...")
        response = requests.get("http://ip-api.com/json/?fields=status,message,country,countryCode,regionName,city,isp,org,as,mobile,proxy,hosting,query", proxies=proxies, timeout=10)
        data = response.json()
        
        if data['status'] != 'success':
            print(f"❌ Error getting IP data: {data.get('message')}")
            return

        ip = data['query']
        country = data['countryCode']
        isp = data['isp']
        is_hosting = data['hosting']
        is_proxy = data['proxy']
        
        print(f"\n📊 RESULTS for {ip}:")
        print(f"   🏳️  Country: {country} {data['country']}")
        print(f"   🏢 ISP: {isp}")
        print(f"   ☁️  Hosting/Datacenter: {'YES ❌' if is_hosting else 'NO ✅'}")
        print(f"   🛡️  Detected as Proxy: {'YES ⚠️' if is_proxy else 'NO ✅'}")
        
        print("\n⚖️  SHEERID VERDICT:")
        
        score = 0
        reasons = []
        
        # Rule 1: Must be US
        if country != 'US':
            score -= 50
            reasons.append("❌ Not a US IP (SheerID requires US for US offers)")
        else:
            score += 20
            
        # Rule 2: Datacenter/Hosting is BAD
        if is_hosting:
            score -= 40
            reasons.append("❌ Detected as Datacenter/Hosting (AWS, DigitalOcean, etc are mostly blocked)")
        else:
            score += 30
            
        # Rule 3: Known Bad ISPs
        bad_keywords = ['Google', 'Amazon', 'Microsoft', 'Datacenter', 'Cloud', 'M247', 'DigitalOcean', 'Linode']
        if any(keyword.lower() in isp.lower() for keyword in bad_keywords):
            score -= 30
            reasons.append(f"❌ ISP '{isp}' is known for bots")
        else:
            score += 10
            
        # Rule 4: Consumer ISP Bonus
        good_keywords = ['Comcast', 'Verizon', 'AT&T', 'T-Mobile', 'Spectrum', 'Charter', 'Cox']
        if any(keyword.lower() in isp.lower() for keyword in bad_keywords):
            score += 40
            reasons.append("✅ Looks like a Residential/Consumer ISP")

        if score > 30:
            print("   ✅ GOOD IP! High chance of success.")
        elif score > 0:
            print("   ⚠️  OKAY IP. Might work, might fail.")
        else:
            print("   ❌ BAD IP. Almost guaranteed to fail.")
            
        if reasons:
            print("\n📝 Details:")
            for r in reasons:
                print(f"   {r}")
                
        print("\n💡 TIP: For SheerID, use 'Residential Proxies' containing ISPs like Comcast, AT&T, or Verizon.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_ip()
