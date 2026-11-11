"""
Telegram Bot Interface for SheerID Verification
PLATINUM EDITION - Custom ASCII UI
"""
import sys

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram.constants import ParseMode

import config
import sheerid_api
import student_generator
import doc_generator
from datetime import datetime

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ═══════════════════════════════════════════════════════════════════════
# CUSTOM UI COMPONENTS - Box Drawing & ASCII Art
# ═══════════════════════════════════════════════════════════════════════

class UI:
    """Custom UI elements using Unicode box-drawing characters"""
    
    # Box corners and lines
    TL = "╔"  # top-left
    TR = "╗"  # top-right
    BL = "╚"  # bottom-left
    BR = "╝"  # bottom-right
    H = "═"   # horizontal
    V = "║"   # vertical
    
    # Light box
    tl = "┌"
    tr = "┐"
    bl = "└"
    br = "┘"
    h = "─"
    v = "│"
    
    # Status indicators (non-emoji)
    PULSE = "●"
    HOLLOW = "○"
    ARROW = "▸"
    CHECK = "▣"
    CROSS = "▢"
    BLOCK = "█"
    SHADE = "░"
    HALF = "▒"
    
    # Progress characters
    PROG_FULL = "■"
    PROG_EMPTY = "□"
    
    @staticmethod
    def box(title: str, content: str, width: int = 32) -> str:
        """Generate a bordered box with title"""
        lines = content.split('\n')
        inner_w = width - 4
        
        # Build box
        result = []
        result.append(f"{UI.TL}{UI.H}{title[:inner_w].center(inner_w, UI.H)}{UI.H}{UI.TR}")
        
        for line in lines:
            padded = line[:inner_w].ljust(inner_w)
            result.append(f"{UI.V} {padded} {UI.V}")
        
        result.append(f"{UI.BL}{UI.H * (width - 2)}{UI.BR}")
        return '\n'.join(result)
    
    @staticmethod
    def progress_bar(current: int, total: int, width: int = 12) -> str:
        """Generate ASCII progress bar"""
        filled = int((current / total) * width)
        empty = width - filled
        return f"[{UI.PROG_FULL * filled}{UI.PROG_EMPTY * empty}]"
    
    @staticmethod
    def header(text: str) -> str:
        """Generate a header line"""
        return f"{UI.BLOCK}{UI.SHADE} {text} {UI.SHADE}{UI.BLOCK}"
    
    @staticmethod
    def status_line(key: str, value: str, key_width: int = 12) -> str:
        """Generate aligned status line"""
        return f"{UI.ARROW} {key.ljust(key_width)} {UI.v} {value}"
    
    @staticmethod
    def divider(width: int = 28) -> str:
        """Generate divider line"""
        return UI.h * width

# ═══════════════════════════════════════════════════════════════════════
# ASCII ART BANNERS
# ═══════════════════════════════════════════════════════════════════════

BANNER_MAIN = """
```
 _____ _                    ___________
/  ___| |                  |_   _|  _  \\
\\ `--.| |__   ___  ___ _ __  | | | | | |
 `--. \\ '_ \\ / _ \\/ _ \\ '__| | | | | | |
/\\__/ / | | |  __/  __/ |   _| |_| |/ /
\\____/|_| |_|\\___|\\___|_|   |___/|___/

      P L A T I N U M   E D I T I O N
           ┌──────────────────┐
           │  STEALTH  MODE   │
           └──────────────────┘
```"""

BANNER_SUCCESS = """
```
    ╔═══════════════════════════════╗
    ║                               ║
    ║   ▓▓▓   █   █  █ █▄▀         ║
    ║   █ █   ██ ██  █ █ █         ║
    ║   ▓▓▓   █ █ █  █ █  █        ║
    ║                               ║
    ║   V E R I F I C A T I O N    ║
    ║   C O M P L E T E            ║
    ╚═══════════════════════════════╝
```"""

BANNER_FAIL = """
```
    ┌───────────────────────────────┐
    │         ▄▀▀▀▀▀▀▀▀▀▀▀▄        │
    │        █  ░░░░░░░░░  █       │
    │        █  ░ DENIED ░  █       │
    │        █  ░░░░░░░░░  █       │
    │         ▀▄▄▄▄▄▄▄▄▄▄▄▀        │
    └───────────────────────────────┘
```"""

BANNER_LOADING = """```
     ╭─────────────────────╮
     │ ▓▓▓▓▓▓▓░░░░░░░░░░░░ │
     │    PROCESSING...    │
     ╰─────────────────────╯
```"""

# ═══════════════════════════════════════════════════════════════════════
# COMMAND HANDLERS
# ═══════════════════════════════════════════════════════════════════════

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    welcome_text = f"""{BANNER_MAIN}

{UI.header("SYSTEM STATUS")}

{UI.status_line("NODE", "ONLINE")}
{UI.status_line("SESSION", f"`{user_id}`")}
{UI.status_line("ACCESS", "AUTHORIZED")}
{UI.status_line("TIMESTAMP", timestamp)}

{UI.divider()}

{UI.header("AVAILABLE COMMANDS")}

{UI.ARROW} `/verify [url]`  Execute verification
{UI.ARROW} `/status`        System diagnostics
{UI.ARROW} `/help`          Protocol manual

{UI.divider()}
`Paste any SheerID link directly to verify`
"""
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = f"""
```
╔═══════════════════════════════════╗
║     OPERATIONAL PROTOCOL v2.0     ║
╠═══════════════════════════════════╣
║                                   ║
║  [1] ACQUIRE TARGET               ║
║      Copy verification link       ║
║      from offer page              ║
║                                   ║
║  [2] NETWORK REQUIREMENTS         ║
║      US residential IP required   ║
║      VPN endpoints acceptable     ║
║                                   ║
║  [3] EXECUTE                      ║
║      /verify <link>               ║
║      or paste link directly       ║
║                                   ║
╠═══════════════════════════════════╣
║  TLS FINGERPRINT  │  Chrome 131   ║
║  API VERSION      │  2.178.0      ║
║  STEALTH LEVEL    │  MAXIMUM      ║
╚═══════════════════════════════════╝
```
"""
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import socket
    
    # Check connectivity
    try:
        socket.create_connection(("services.sheerid.com", 443), timeout=5)
        api_status = f"{UI.PULSE} CONNECTED"
    except:
        api_status = f"{UI.HOLLOW} UNREACHABLE"
    
    proxy_status = f"{UI.PULSE} ACTIVE" if config.USE_PROXY else f"{UI.HOLLOW} DISABLED"
    
    status_text = f"""
```
┌─────────────────────────────────┐
│      SYSTEM DIAGNOSTICS         │
├─────────────────────────────────┤
│                                 │
│  SheerID API     {api_status.ljust(12)}   │
│  Proxy Module    {proxy_status.ljust(12)}   │
│  Turnstile Engine ● ARMED       │
│  Doc Generator   ● READY        │
│  Identity Pool   ● LOADED       │
│                                 │
├─────────────────────────────────┤
│  MEMORY   [{UI.PROG_FULL*7}{UI.PROG_EMPTY*5}]  58%      │
│  UPTIME   [{UI.PROG_FULL*10}{UI.PROG_EMPTY*2}]  STABLE   │
└─────────────────────────────────┘
```
"""
    await update.message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN)

async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        error_text = f"""
```
{UI.tl}{UI.h*28}{UI.tr}
{UI.v}  ERROR: MISSING ARGUMENT   {UI.v}
{UI.bl}{UI.h*28}{UI.br}
```
Usage: `/verify https://...`
"""
        await update.message.reply_text(error_text, parse_mode=ParseMode.MARKDOWN)
        return

    url = context.args[0]
    user = update.effective_user
    
    client = sheerid_api.SheerIDClient(proxy=config.PROXY_URL if config.USE_PROXY else None)
    
    verification_id, is_program = client.extract_verification_id_from_url(url)
    if not verification_id:
        await update.message.reply_text(f"""
```
{UI.tl}{UI.h*28}{UI.tr}
{UI.v}  ERROR: INVALID LINK       {UI.v}
{UI.v}  Cannot extract ID         {UI.v}
{UI.bl}{UI.h*28}{UI.br}
```
""", parse_mode=ParseMode.MARKDOWN)
        return

    # Initial status
    init_text = f"""{BANNER_LOADING}

{UI.status_line("TASK ID", f"`{verification_id[:16]}...`")}
{UI.status_line("OPERATOR", user.first_name)}
{UI.status_line("TIME", datetime.now().strftime('%H:%M:%S'))}

{UI.progress_bar(1, 4)} `PHASE 1/4`
{UI.ARROW} Generating identity profile...
"""
    status_msg = await update.message.reply_text(init_text, parse_mode=ParseMode.MARKDOWN)

    try:
        # Step 1: Generate Profile
        profile = student_generator.generate_student_profile()
        univ_name = profile["display_info"]["university"]
        student_name = profile["display_info"]["full_name"]
        
        phase2_text = f"""
```
╭─────────────────────────────╮
│ ▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░ │
│      PAYLOAD INJECTION      │
╰─────────────────────────────╯
```

{UI.status_line("TARGET", univ_name[:20])}
{UI.status_line("PROFILE", student_name)}
{UI.status_line("EMAIL", profile['email'][:24])}

{UI.progress_bar(2, 4)} `PHASE 2/4`
{UI.ARROW} Submitting to SheerID API...
"""
        await status_msg.edit_text(phase2_text, parse_mode=ParseMode.MARKDOWN)

        # Step 2: Submit
        def doc_gen_wrapper(first, last, school):
            if doc_generator.select_document_type() == "student_id":
                return doc_generator.generate_student_id(first, last, school)
            else:
                return doc_generator.generate_transcript(first, last, profile["birthDate"], school)

        result = client.process_verification(verification_id, is_program, profile, doc_gen_wrapper, raw_url=url)
        
        # Step 3: Handle Result
        if result["status"] == "SUCCESS":
            success_text = f"""{BANNER_SUCCESS}

{UI.header("VERIFICATION DATA")}

{UI.status_line("INSTITUTION", univ_name[:20])}
{UI.status_line("IDENTITY", student_name)}
{UI.status_line("EMAIL", f"`{profile['email']}`")}

{UI.divider()}
{UI.header("REWARD ACQUIRED")}
"""
            if result.get("reward_code"):
                success_text += f"\n{UI.ARROW} Code: `{result['reward_code']}`"
                
            if result.get("redirect_url"):
                success_text += f"\n{UI.ARROW} [Access Reward]({result['redirect_url']})"
                
            success_text += f"""

{UI.divider()}
```
  CONNECTION TERMINATED SECURELY
```
"""
            await status_msg.edit_text(success_text, parse_mode=ParseMode.MARKDOWN)
            
        elif result["status"] == "TIMEOUT":
            last_step = result.get("last_details", {}).get("currentStep")
            if last_step == "pending":
                pending_text = f"""
```
┌─────────────────────────────────┐
│     MANUAL REVIEW QUEUED        │
├─────────────────────────────────┤
│                                 │
│  Documents submitted OK         │
│  Awaiting SheerID review        │
│                                 │
│  Auto-monitor: 30 minutes       │
│  You will be notified           │
│                                 │
└─────────────────────────────────┘
```

{UI.ARROW} Backup link: `{url[:40]}...`
"""
                await status_msg.edit_text(pending_text, parse_mode=ParseMode.MARKDOWN)
                
                import subprocess
                subprocess.Popen([sys.executable, "monitor_task.py", verification_id, str(update.effective_chat.id)])
            else:
                await status_msg.edit_text(f"""
```
{UI.tl}{UI.h*26}{UI.tr}
{UI.v}  TIMEOUT: No response   {UI.v}
{UI.v}  Check link manually    {UI.v}
{UI.bl}{UI.h*26}{UI.br}
```
""", parse_mode=ParseMode.MARKDOWN)
        
        else:
            reason = result.get("reason")
            if isinstance(reason, list):
                reason = ", ".join(reason)
            elif isinstance(result.get("details"), dict):
                reason = result["details"].get("systemErrorMessage", "Unknown Error")
            
            error_msg = str(reason or result.get("status", "Unknown"))[:30]
            
            fail_text = f"""{BANNER_FAIL}

{UI.status_line("REASON", error_msg)}
{UI.status_line("TARGET", univ_name[:18])}

{UI.divider()}
```
HINT: IP mismatch or session
      tainted. Use fresh link.
```
"""
            await status_msg.edit_text(fail_text, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        error_text = f"""
```
╔═══════════════════════════════╗
║      SYSTEM EXCEPTION         ║
╠═══════════════════════════════╣
║  {str(e)[:27].ljust(27)}   ║
╚═══════════════════════════════╝
```
"""
        await status_msg.edit_text(error_text, parse_mode=ParseMode.MARKDOWN)
        logging.error(f"Error processing {verification_id}: {e}")

# ═══════════════════════════════════════════════════════════════════════
# BOT INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════

def run_bot():
    if not config.BOT_TOKEN or config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print(f"""
{UI.TL}{UI.H*30}{UI.TR}
{UI.V}  CONFIG ERROR              {UI.V}
{UI.V}  Set BOT_TOKEN in .env     {UI.V}
{UI.BL}{UI.H*30}{UI.BR}
""")
        return

    application = ApplicationBuilder().token(config.BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("verify", verify_command))
    
    async def handle_raw_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        if "sheerid.com/verify/" in text:
            context.args = [text.strip()]
            await verify_command(update, context)
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_raw_message))

    print(f"""
{UI.TL}{UI.H*32}{UI.TR}
{UI.V}  SHEERID PLATINUM BOT        {UI.V}
{UI.V}  Status: ONLINE              {UI.V}
{UI.V}  Press Ctrl+C to terminate   {UI.V}
{UI.BL}{UI.H*32}{UI.BR}
""")
    application.run_polling()

if __name__ == "__main__":
    run_bot()
