
import sys
import os

# Add the cloned repo to path
sys.path.append("/tmp/ref_bot")

from one.sheerid_verifier import SheerIDVerifier
import config

# Use the proxy if available
proxy = os.environ.get("PROXY_URL")

def test():
    # Use the ID the user is stuck with
    vid = "67c8c14f5f17a83b745e3f82"
    print(f"Testing Reference Bot Logic with ID: {vid}")
    
    verifier = SheerIDVerifier(vid)
    # We need to monkeypatch the http client if we want proxy
    # For now let's just run it
    try:
        result = verifier.verify()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
