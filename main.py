import os
import re
import requests
import asyncio
from pyrogram import Client, filters

# GitHub Secrets
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

app = Client("terabox_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Terabox லிங்குகளை அடையாளம் காணும் முறை
def is_terabox(url):
    domains = [
        r"terabox\.com", r"nephobox\.com", r"4funbox\.com", r"mirrobox\.com", 
        r"momerybox\.com", r"teraboxapp\.com", r"1024tera\.com", r"freeterabox\.com"
    ]
    return any(re.search(domain, url) for domain in domains)

def get_download_link(url):
    """Terabox லிங்கிலிருந்து நேரடி வீடியோ லிங்க் எடுக்கும் பகுதி."""
    try:
        # லிங்கை சரிசெய்தல்
        if "terabox.app" in url or "teraboxapp.com" in url:
            url = url.replace("terabox.app", "1024terabox.com").replace("teraboxapp.com", "1024terabox.com")

        api_url = "https://ytshorts.savetube.me/api/v1/terabox-downloader"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://ytshorts.savetube.me",
            "Referer": "https://ytshorts.savetube.me/"
        }
        
        response = requests.post(api_url, headers=headers, json={"url": url}, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            responses = data.get("response", [])
            if responses:
                resolutions = responses[0].get("resolutions", {})
                # HD வீடியோ அல்லது வேகமான டவுன்லோட் லிங்க்
                return resolutions.get("HD Video") or resolutions.get("Fast Download")
        return None
    except Exception as e:
        print(f"API Error: {e}")
        return None

@app.on_message(filters.regex(r'http'))
async def handle_terabox(client, message):
    url = message.text.strip()
    
    if not is_terabox(url):
        return 

    status = await message.reply("⏳ **Terabox வீடியோவைத் தேடுகிறேன்...**")
    
    # டவுன்லோட் லிங்க் பெறுதல்
    download_link = get_download_link(url)
    
    if download_link:
        await status.edit("✅ லிங்க் கிடைத்துவிட்டது! அனுப்பப்படுகிறது...")
        try:
            # வீடியோவை நேரடியாக டெலிகிராமிற்கு அனுப்புதல்
            await message.reply_video(
                video=download_link,
                caption="✨ **Unga Terabox Video Ready!**"
            )
            await status.delete()
        except Exception as e:
            await status.edit(f"❌ பிழை: வீடியோவை அனுப்ப முடியவில்லை. நேரடி லிங்க் இதோ:\n\n{download_link}")
    else:
        await status.edit("❌ மன்னிக்கவும்! வீடியோ லிங்க் கிடைக்கவில்லை. சில நிமிடங்கள் கழித்து மீண்டும் முயலவும்.")

print("Terabox Bot Started Successfully...")
app.run()
