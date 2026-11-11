
import asyncio
import logging
import sheerid_api
import config
from telegram import Bot
from telegram.constants import ParseMode

logging.basicConfig(level=logging.INFO)

async def monitor_pending_verification(verification_id, chat_id):
    """Monitors a pending verification for up to 30 minutes"""
    client = sheerid_api.SheerIDClient(proxy=config.PROXY_URL if config.USE_PROXY else None)
    
    # Configure Bot
    bot = Bot(token=config.BOT_TOKEN)
    
    logging.info(f"[*] Starting monitor for {verification_id} (Chat: {chat_id})")
    
    # Poll every 1 minute for 30 minutes
    for i in range(30):
        try:
            logging.info(f"Checking status for {verification_id} (Attempt {i+1}/30)...")
            details = client.get_verification_details(verification_id)
            step = details.get("currentStep")
            
            if step == "success":
                # SUCCESS!
                reward = details.get("rewardCode", "CODE_NOT_FOUND")
                msg = (
                    f"🎉 **VERIFICATION APPROVED!**\n\n"
                    f"🆔 `{verification_id}`\n"
                    f"🎁 **Reward Code:** `{reward}`\n"
                    f"🔗 [Claim Offer]({details.get('redirectUrl', '')})"
                )
                await bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.MARKDOWN)
                logging.info(f"SUCCESS detected for {verification_id}")
                return
                
            elif step == "error" or details.get("errorIds"):
                # FAILED
                errors = details.get("errorIds", [])
                msg = (
                    f"❌ **Verification Rejected**\n\n"
                    f"🆔 `{verification_id}`\n"
                    f"Reason: {errors}"
                )
                await bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.MARKDOWN)
                logging.info(f"REJECT detected for {verification_id}")
                return
                
            # If still pending/docUpload, continue waiting
            await asyncio.sleep(60)
            
        except Exception as e:
            logging.error(f"Error checking status: {e}")
            await asyncio.sleep(60)

    # If loop finishes without result
    await bot.send_message(
        chat_id=chat_id, 
        text=f"⚠️ **Monitor Timeout** for `{verification_id}`.\nPlease check manually.", 
        parse_mode=ParseMode.MARKDOWN
    )

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python3 monitor_task.py <verification_id> <chat_id>")
        sys.exit(1)
        
    vid = sys.argv[1]
    cid = sys.argv[2]
    
    asyncio.run(monitor_pending_verification(vid, cid))
