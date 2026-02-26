import os
import re
import requests
import asyncio
import time
from pyrogram import Client, filters

# GitHub Secrets மூலம் வரும் தகவல்கள்
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# பாட்டைத் தொடங்குதல்
app = Client("terabox_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Terabox லிங்குகளை அடையாளம் காணும் லிஸ்ட்
TERABOX_DOMAINS = [
    r"terabox\.com", r"nephobox\.com", r"4funbox\.com", r"mirrobox\.com", 
    r"momerybox\.com", r"teraboxapp\.com", r"1024tera\.com", r"freeterabox\.com"
]

def is_terabox(url):
    """கொடுக்கப்பட்ட லிங்க் Terabox தானா என்று சரிபார்க்கும்."""
    for pattern in TERABOX_DOMAINS:
        if re.search(pattern, url):
            return True
    return False

def get_download_link(url):
    """Terabox லிங்கிலிருந்து டவுன்லோட் லிங்க் எடுக்கும் பகுதி."""
    try:
        # நீங்கள் அனுப்பிய GitHub கோப்பில் உள்ள அதே API முறை
        api_url = "https://ytshorts.savetube.me/api/v1/terabox-downloader"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        
        # நெட்வொர்க் வழியாக டேட்டா கோரப்படுகிறது
        response = requests.post(api_url, headers=headers, json={"url": url})
        
        if response.status_code == 200:
            data = response.json()
            # API பதிலிலிருந்து வீடியோ லிங்க் எடுக்கப்படுகிறது
            responses = data.get("response", [])
            if responses:
                resolutions = responses[0].get("resolutions", {})
                # 'HD Video' அல்லது 'Fast Download' லிங்க் எடுக்கப்படும்
                return resolutions.get("HD Video") or resolutions.get("Fast Download")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.on_message(filters.regex(r'http'))
async def handle_terabox(client, message):
    url = message.text.strip()
    
    if not is_terabox(url):
        return # Terabox லிங்க் இல்லையென்றால் பதில் அளிக்காது

    status = await message.reply("⏳ **Terabox வீடியோவைத் தேடுகிறேன்...**")
    
    # டவுன்லோட் லிங்க் பெறுதல்
    download_link = get_download_link(url)
    
    if download_link:
        await status.edit("✅ லிங்க் கிடைத்துவிட்டது! அனுப்பப்படுகிறது...")
        try:
            # வீடியோவை நேரடியாக டெலிகிராமிற்கு அனுப்புதல்
            await message.reply_video(
                video=download_link,
                caption="✨ **Unga Terabox Video Ready!**\n\nJoin: @MyChannel"
            )
            await status.delete()
        except Exception as e:
            await status.edit(f"❌ பிழை: வீடியோவை அனுப்ப முடியவில்லை. நேரடி லிங்க் இதோ:\n{download_link}")
    else:
        await status.edit("❌ மன்னிக்கவும்! வீடியோ லிங்க் கிடைக்கவில்லை. மீண்டும் முயற்சி செய்யுங்கள்.")

print("Bot is running...")
app.run()
