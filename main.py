#!/usr/bin/env python3
"""
SheerID Verification Tool - Platinum Edition
Entry Point
"""
import argparse
import sys
from datetime import datetime

import config
import sheerid_api
import student_generator
import doc_generator
# Import bot module lazily if needed, but here we import to check availability
try:
    import telegram_bot
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

def cli_verification(link):
    print("="*60)
    print("SheerID Auto Verifier - CLI Mode")
    print("="*60)
    
    client = sheerid_api.SheerIDClient(proxy=config.PROXY_URL if config.USE_PROXY else None)
    
    verification_id, is_program = client.extract_verification_id_from_url(link)
    if not verification_id:
        print("❌ Error: Invalid URL. Could not extract verification ID.")
        return
        
    print(f"[*] Target ID: {verification_id}")
    
    # 2. Generate Profile
    print("[*] Generating student profile...")
    profile = student_generator.generate_student_profile()
    print(f"    Name: {profile['display_info']['full_name']}")
    print(f"    Univ: {profile['display_info']['university']}")
    print(f"    Email: {profile['email']}")
    print(f"    DOB: {profile['birthDate']}")
    
    # 3. Process
    print("\n[*] Starting verification process...")
    
    def doc_gen_wrapper(first, last, school):
         print("    [!] Generating document evidence...")
         if doc_generator.select_document_type() == "student_id":
             return doc_generator.generate_student_id(first, last, school)
         else:
             return doc_generator.generate_transcript(first, last, profile["birthDate"], school)

    result = client.process_verification(verification_id, is_program, profile, doc_gen_wrapper)
    
    print("\n" + "="*60)
    print(f"RESULT: {result['status']}")
    print("="*60)
    
    if result["status"] == "SUCCESS":
        print(f"✅ SUCCESS!")
        if result.get("reward_code"):
            print(f"🎁 Reward Code: {result['reward_code']}")
        if result.get("redirect_url"):
            print(f"🔗 Claim Link: {result['redirect_url']}")
    else:
        print(f"❌ FAILED")
        print(f"Reason: {result.get('errors', result.get('reason'))}")
        
def main():
    parser = argparse.ArgumentParser(description="SheerID Verification Tool")
    parser.add_argument("--bot", action="store_true", help="Run in Telegram Bot mode")
    parser.add_argument("--verify", type=str, help="Verify a specific link (CLI mode)")
    parser.add_argument("--test-gen", action="store_true", help="Test student data generation")
    
    args = parser.parse_args()
    
    if args.bot:
        if not TELEGRAM_AVAILABLE:
            print("❌ Error: telegram-bot library not found. Install with: pip install python-telegram-bot")
            return
        telegram_bot.run_bot()
        
    elif args.verify:
        cli_verification(args.verify)
        
    elif args.test_gen:
        print(student_generator.generate_student_profile())
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
