"""
Configuration settings for SheerID Verification Bot
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Token (Loaded from .env for security)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

# SheerID API Settings
SHEERID_API_URL = "https://services.sheerid.com/rest/v2"
REFERRER_URL = "https://verify.sheerid.com/"

# Connection Settings
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30  # seconds

# Verification Settings
AGE_MIN = 18
AGE_MAX = 24
COUNTRY = "US"

# Anti-Detect Settings
USE_PROXY = os.getenv("USE_PROXY", "False").lower() in ("true", "1", "yes")
PROXY_URL = os.getenv("PROXY_URL", "").strip()

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "bot_activity.log"
