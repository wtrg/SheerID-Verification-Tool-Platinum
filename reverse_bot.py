#!/usr/bin/env python3
"""
Reverse Engineer Telegram Bot - Intercept responses dari @AutoGeminiProbot
"""

import asyncio
import os
from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# API Credentials from environment
API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
SESSION_NAME = "telegram_session"

# Target Bot
TARGET_BOT = "AutoGeminiProbot"

async def main():
    print("=" * 60)
    print("🔍 REVERSE ENGINEERING: @AutoGeminiProbot")
    print("=" * 60)
    
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()
    
    me = await client.get_me()
    print(f"\n✅ Logged in as: {me.first_name} (@{me.username})")
    
    # Get bot entity
    bot = await client.get_entity(TARGET_BOT)
    print(f"\n📌 Target Bot:")
    print(f"   Name: {bot.first_name}")
    print(f"   Username: @{bot.username}")
    print(f"   ID: {bot.id}")
    print(f"   Is Bot: {bot.bot}")
    
    responses = []
    
    # Test commands
    test_commands = [
        "/start",
        "/help",
        "/gemini",
        "/verify",
        "/status",
        "/info",
        "/quota",
        "/ping",
    ]
    
    print(f"\n{'=' * 60}")
    print("📨 SENDING TEST COMMANDS...")
    print("=" * 60)
    
    for cmd in test_commands:
        print(f"\n>>> Sending: {cmd}")
        await client.send_message(bot, cmd)
        
        # Wait for response
        await asyncio.sleep(3)
        
        # Get last messages from bot
        async for message in client.iter_messages(bot, limit=3):
            if message.out:  # Skip our own messages
                continue
            
            response_data = {
                "command": cmd,
                "response_id": message.id,
                "response_text": message.text,
                "response_date": message.date.isoformat(),
                "has_buttons": bool(message.buttons),
                "buttons": []
            }
            
            # Extract button info if present
            if message.buttons:
                for row in message.buttons:
                    for btn in row:
                        response_data["buttons"].append({
                            "text": btn.text,
                            "data": str(btn.data) if hasattr(btn, 'data') else None,
                            "url": btn.url if hasattr(btn, 'url') else None,
                        })
            
            responses.append(response_data)
            
            print(f"<<< Response ({message.id}):")
            print(f"    {message.text[:200] if message.text else '[No text]'}...")
            if message.buttons:
                print(f"    [Has {len([b for r in message.buttons for b in r])} buttons]")
            break
    
    # Save results
    output = {
        "scraped_at": datetime.now().isoformat(),
        "bot_info": {
            "name": bot.first_name,
            "username": bot.username,
            "id": bot.id,
        },
        "responses": responses
    }
    
    with open("bot_reverse_data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'=' * 60}")
    print(f"✅ Data saved to: bot_reverse_data.json")
    print("=" * 60)
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
