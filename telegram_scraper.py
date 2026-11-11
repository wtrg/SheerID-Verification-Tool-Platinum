#!/usr/bin/env python3
"""
Telegram Scraper - Mengumpulkan info dari grup/channel Telegram
"""

import asyncio
import os
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import Channel, Chat, User
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# API Credentials from environment
API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")

# Session file
SESSION_NAME = "telegram_session"

# Target groups/channels/bots
TARGETS = [
    "infosatsetgrup",      # https://t.me/infosatsetgrup
    "AutoGeminiProbot",    # Bot
    "sgopen_bot",          # Bot
    "infosatsetcuy",       # https://t.me/infosatsetcuy
]

async def get_entity_info(client, target):
    """Get detailed info about an entity"""
    try:
        entity = await client.get_entity(target)
        
        info = {
            "target": target,
            "type": type(entity).__name__,
            "id": entity.id,
        }
        
        if isinstance(entity, Channel):
            info["title"] = entity.title
            info["username"] = entity.username
            info["megagroup"] = entity.megagroup
            info["broadcast"] = entity.broadcast
            info["participants_count"] = getattr(entity, 'participants_count', 'N/A')
            
            # Get full channel info
            try:
                full = await client(GetFullChannelRequest(entity))
                info["about"] = full.full_chat.about
                info["participants_count"] = full.full_chat.participants_count
            except Exception as e:
                info["full_info_error"] = str(e)
                
        elif isinstance(entity, User):
            info["first_name"] = entity.first_name
            info["last_name"] = entity.last_name
            info["username"] = entity.username
            info["bot"] = entity.bot
            info["verified"] = entity.verified
            
        elif isinstance(entity, Chat):
            info["title"] = entity.title
            info["participants_count"] = getattr(entity, 'participants_count', 'N/A')
            
        return info
        
    except Exception as e:
        return {
            "target": target,
            "error": str(e)
        }

async def get_recent_messages(client, target, limit=50):
    """Get recent messages from a channel/group"""
    try:
        entity = await client.get_entity(target)
        
        messages = []
        async for message in client.iter_messages(entity, limit=limit):
            msg_data = {
                "id": message.id,
                "date": message.date.isoformat() if message.date else None,
                "text": message.text,
                "views": message.views,
                "forwards": message.forwards,
            }
            
            if message.sender:
                msg_data["sender"] = {
                    "id": message.sender.id,
                    "name": getattr(message.sender, 'first_name', None) or getattr(message.sender, 'title', None),
                    "username": getattr(message.sender, 'username', None),
                }
                
            messages.append(msg_data)
            
        return messages
        
    except Exception as e:
        return {"error": str(e)}

async def main():
    print("=" * 60)
    print("TELEGRAM INFO SCRAPER")
    print("=" * 60)
    
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    
    await client.start()
    
    me = await client.get_me()
    print(f"\n✅ Logged in as: {me.first_name} (@{me.username})")
    print(f"   Phone: {me.phone}")
    print(f"   User ID: {me.id}")
    
    all_data = {
        "scraped_at": datetime.now().isoformat(),
        "logged_in_as": {
            "name": me.first_name,
            "username": me.username,
            "id": me.id,
        },
        "targets": {}
    }
    
    print("\n" + "=" * 60)
    print("GATHERING INFORMATION FROM TARGETS...")
    print("=" * 60)
    
    for target in TARGETS:
        print(f"\n📌 Processing: {target}")
        print("-" * 40)
        
        # Get entity info
        info = await get_entity_info(client, target)
        
        if "error" not in info:
            print(f"   Type: {info.get('type')}")
            print(f"   Title/Name: {info.get('title') or info.get('first_name', 'N/A')}")
            print(f"   Username: @{info.get('username', 'N/A')}")
            print(f"   ID: {info.get('id')}")
            
            if info.get('about'):
                print(f"   About: {info.get('about')[:100]}...")
                
            if info.get('participants_count'):
                print(f"   Members: {info.get('participants_count')}")
                
            if info.get('bot'):
                print(f"   Is Bot: ✅")
                
            # Get messages if it's a channel/group
            if info.get('type') in ['Channel', 'Chat']:
                print(f"\n   📝 Fetching recent messages...")
                messages = await get_recent_messages(client, target, limit=30)
                
                if isinstance(messages, list):
                    info["recent_messages"] = messages
                    print(f"   Found {len(messages)} messages")
                    
                    # Print some recent messages
                    print("\n   🔥 RECENT MESSAGES:")
                    for msg in messages[:10]:
                        if msg.get('text'):
                            text = msg['text'][:100].replace('\n', ' ')
                            sender = msg.get('sender', {}).get('name', 'Unknown')
                            print(f"   [{msg['date'][:10]}] {sender}: {text}...")
                else:
                    info["messages_error"] = messages.get("error")
        else:
            print(f"   ❌ Error: {info.get('error')}")
            
        all_data["targets"][target] = info
        
    # Save to JSON
    output_file = "telegram_scraped_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
        
    print(f"\n\n{'=' * 60}")
    print(f"✅ Data saved to: {output_file}")
    print(f"{'=' * 60}")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
