import uuid
from pyrogram import Client, filters
from motor.motor_asyncio import AsyncIOMotorClient

# Bot Credentials
API_ID = 1234567               # Apne telegram account ka API ID dalein
API_HASH = "YOUR_API_HASH"     # Apne telegram account ka API HASH dalein
BOT_TOKEN = "YOUR_BOT_TOKEN"   # @BotFather se mila hua Token

# Database Setup (Same wahi DB use karein jo index.py me kiya hai)
MONGO_URI = "YOUR_MONGODB_URI_HERE"
db_client = AsyncIOMotorClient(MONGO_URI)
db = db_client["bypass_protector"]
links_col = db["links"]

# Aapka Vercel ka live App URL
VERCEL_APP_URL = "https://your-app-name.vercel.app"

bot = Client("bypass_protector_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start"))
async def start_cmd(client, message):
    await message.reply_text("👋 Hello! Mujhe koi bhi normal link bhejo, main use **Bypass-Proof Protected Link** me badal dunga.")

@bot.on_message(filters.regex(r"https?://\S+"))
async def protect_link_handler(client, message):
    original_url = message.text.strip()
    
    # 1. Ek chota unique random ID generate karna
    unique_id = str(uuid.uuid4())[:8]
    
    # 2. Database me original link ko save karna
    await links_col.insert_one({
        "_id": unique_id,
        "original_url": original_url
    })
    
    # 3. Vercel ka protected link ready karna
    protected_url = f"{VERCEL_APP_URL}/visit?id={unique_id}"
    
    # 4. User ko response send karna
    response_text = (
        "🔒 **Link Successfully Protected!**\n\n"
        f"**Original Link:** {original_url}\n"
        f"**Protected Link:** `{protected_url}`\n\n"
        "⚠️ *Note: Yeh link sirf ek baar open ho sakti hai aur bina captcha solve kiye koi bypass nahi kar payega.*"
    )
    
    await message.reply_text(response_text, disable_web_page_preview=True)

print("Bot is starting...")
bot.run()
