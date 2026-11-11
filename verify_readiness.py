import sys
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import time
import json
import requests
from pathlib import Path

def print_status(msg, status="INFO"):
    colors = {
        "INFO": "\033[94m[INFO]\033[0m",
        "SUCCESS": "\033[92m[SUCCESS]\033[0m",
        "WARN": "\033[93m[WARN]\033[0m",
        "ERROR": "\033[91m[ERROR]\033[0m",
    }
    print(f"{colors.get(status, '[INFO]')} {msg}")

def check_dependencies():
    print_status("Checking dependencies...")
    
    # 1. Pillow
    try:
        from PIL import Image, ImageDraw, ImageFont
        print_status("Pillow is installed.", "SUCCESS")
    except ImportError:
        print_status("Pillow is MISSING. Run: pip install Pillow", "ERROR")
        return False

    # 2. httpx
    try:
        import httpx
        print_status(f"httpx is installed ({httpx.__version__}).", "SUCCESS")
    except ImportError:
        print_status("httpx is MISSING. Run: pip install httpx", "ERROR")
        return False

    # 3. curl_cffi (Highly recommended)
    try:
        import curl_cffi
        print_status("curl_cffi is installed.", "SUCCESS")
    except ImportError:
        print_status("curl_cffi is MISSING. This is critical for avoiding SheerID detection.", "WARN")
        print_status("Recommendation: Run 'pip install curl-cffi'", "INFO")

    return True

def test_doc_generation():
    print_status("Testing document generation...")
    try:
        # Import local functions
        sys.path.append(str(Path(__file__).parent))
        from main_v2 import generate_transcript, generate_student_id
        
        test_dir = Path("test_outputs")
        test_dir.mkdir(exist_ok=True)
        
        # Test Transcript
        t_doc = generate_transcript("Test", "User", "Harvard University", "2002-01-01")
        with open(test_dir / "test_transcript.jpg", "wb") as f:
            f.write(t_doc)
        print_status(f"Transcript generated: {test_dir}/test_transcript.jpg", "SUCCESS")
        
        # Test Student ID
        s_doc = generate_student_id("Test", "User", "Harvard University")
        with open(test_dir / "test_student_id.jpg", "wb") as f:
            f.write(s_doc)
        print_status(f"Student ID generated: {test_dir}/test_student_id.jpg", "SUCCESS")
        
    except Exception as e:
        print_status(f"Document generation failed: {e}", "ERROR")
        return False
    return True

def test_api_connectivity():
    print_status("Testing SheerID API connectivity...")
    try:
        resp = requests.get("https://services.sheerid.com/rest/v2/config", timeout=10)
        if resp.status_code == 200:
            print_status("API is reachable.", "SUCCESS")
        else:
            print_status(f"API returned status {resp.status_code}.", "WARN")
    except Exception as e:
        print_status(f"API connectivity failed: {e}", "ERROR")
        return False
    return True

def check_link_safety(url):
    if not url:
        return
    
    print_status(f"Checking link safety for: {url}")
    try:
        sys.path.append(str(Path(__file__).parent))
        from main_v2 import GeminiVerifier
        
        verifier = GeminiVerifier(url)
        # Using the built-in check_link which is a GET request (SAFE)
        result = verifier.check_link()
        
        if result.get("valid"):
            print_status(f"Link is VALID. Current Step: {result.get('step')}", "SUCCESS")
            print_status("You can safely use this link with the bot.", "SUCCESS")
        else:
            print_status(f"Link Issue: {result.get('error')}", "ERROR")
            
    except Exception as e:
        print_status(f"Failed to check link: {e}", "ERROR")

if __name__ == "__main__":
    print("\n🚀 SheerID Bot Readiness Checker\n" + "="*30)
    
    deps_ok = check_dependencies()
    docs_ok = test_doc_generation()
    api_ok = test_api_connectivity()
    
    print("\n" + "="*30)
    if deps_ok and docs_ok and api_ok:
        print_status("BOT IS READY TO GO!", "SUCCESS")
    else:
        print_status("Bot has some issues. Check the log above.", "ERROR")
    
    print("\nIf you want to check your link safety, run:")
    print("python verify_readiness.py --link YOUR_LINK_HERE")
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--link", help="The verification URL to check")
    args, unknown = parser.parse_known_args()
    
    if args.link:
        check_link_safety(args.link)
