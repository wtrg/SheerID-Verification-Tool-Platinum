"""
Cloudflare Turnstile Local Solver for SheerID (Zero Cost)
Uses Playwright with Stealth engine to execute non-interactive/managed Turnstile challenges locally.
"""

import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import time
import re
import urllib.parse
from typing import Optional, Dict, Tuple
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

def _parse_proxy(proxy_url: Optional[str]) -> Optional[Dict[str, str]]:
    """Parse proxy URL into Playwright proxy dict format"""
    if not proxy_url:
        return None
    try:
        parsed = urllib.parse.urlparse(proxy_url)
        server = f"{parsed.scheme or 'http'}://{parsed.hostname}:{parsed.port}"
        proxy_dict = {"server": server}
        if parsed.username:
            proxy_dict["username"] = urllib.parse.unquote(parsed.username)
        if parsed.password:
            proxy_dict["password"] = urllib.parse.unquote(parsed.password)
        return proxy_dict
    except Exception:
        return {"server": proxy_url}

def solve_sheerid_turnstile(
    target_url_or_id: str,
    program_id: str = "67c8c14f5f17a83b745e3f82",
    proxy: Optional[str] = None,
    timeout: int = 25
) -> Tuple[Optional[str], Optional[str]]:
    """
    Automated zero-cost Turnstile solver for SheerID.
    Returns (captcha_token, resolved_verification_id).
    """
    if target_url_or_id.startswith("http"):
        target_url = target_url_or_id
    else:
        target_url = f"https://services.sheerid.com/verify/{program_id}/?verificationId={target_url_or_id}"
        
    print(f"[*] [Turnstile-Free] Initiating stealth browser for: {target_url[:60]}...")
    proxy_config = _parse_proxy(proxy)
    
    token = None
    resolved_vid = None
    
    # Try extracting verificationId from input URL if already present
    vid_match = re.search(r"verificationId=([a-f0-9]{24})", target_url, re.IGNORECASE)
    if vid_match:
        resolved_vid = vid_match.group(1)
        
    try:
        with Stealth().use_sync(sync_playwright()) as p:
            launch_args = [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-infobars",
            ]
            
            browser = p.chromium.launch(
                headless=True,
                args=launch_args,
                proxy=proxy_config
            )
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                locale="en-US",
                timezone_id="America/New_York",
                device_scale_factor=1,
            )
            
            page = context.new_page()
            
            try:
                page.goto(target_url, wait_until="domcontentloaded", timeout=timeout * 1000)
            except Exception as nav_err:
                print(f"[!] [Turnstile-Free] Navigation warning: {nav_err}")
                
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                # Check current page URL in case SheerID updated or redirected to ?verificationId=...
                current_url = page.url
                if not resolved_vid:
                    curr_match = re.search(r"verificationId=([a-f0-9]{24})", current_url, re.IGNORECASE)
                    if curr_match:
                        resolved_vid = curr_match.group(1)
                        print(f"[*] [Turnstile-Free] Extracted real session verificationId: {resolved_vid}")
                
                # Check for standard Turnstile response input
                token = page.evaluate("""() => {
                    const el = document.querySelector('[name="cf-turnstile-response"]') || 
                               document.querySelector('[name="turnstileToken"]') ||
                               document.querySelector('input[type="hidden"][name*="turnstile"]');
                    if (el && el.value && el.value.length > 20) return el.value;
                    return null;
                }""")
                
                if token:
                    elapsed = round(time.time() - start_time, 1)
                    print(f"[+] [Turnstile-Free] Token acquired successfully in {elapsed}s! (len={len(token)})")
                    break
                    
                # Check if an interactive challenge checkbox needs a click
                try:
                    for frame in page.frames:
                        if "challenges.cloudflare.com" in frame.url:
                            checkbox = frame.locator("input[type=checkbox], .ctp-checkbox-label, #challenge-stage")
                            if checkbox.count() > 0 and checkbox.first.is_visible():
                                print("[*] [Turnstile-Free] Interactive checkbox detected! Clicking naturally...")
                                checkbox.first.click(delay=120)
                                time.sleep(1)
                except Exception:
                    pass
                    
                time.sleep(0.8)
                
            browser.close()
            return token, resolved_vid
            
    except Exception as e:
        print(f"[!] [Turnstile-Free] Solver encountered error: {e}")
        return None, resolved_vid

if __name__ == "__main__":
    test_target = sys.argv[1] if len(sys.argv) > 1 else "https://peet.ws/turnstile-test/non-interactive.html"
    tok, vid = solve_sheerid_turnstile(test_target)
    print("Result token:", tok[:30] if tok else None, "len:", len(tok) if tok else 0, "vid:", vid)
