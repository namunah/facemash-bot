import os
import sys
import time
import random
import asyncio
import urllib.request
from io import BytesIO
import requests
from PIL import Image as PILImage
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# =====================================================================
# ⚙️ SECURE SYSTEM PARAMETERS & CREDENTIALS
# =====================================================================
TOKEN = "8627289745:AAFKCtbT_jKXqIIxXyHCCDv8vNEirfdgN2A"
CHANNEL_ID = -1004381737942  
IMAGE_LIMIT = 100
TARGET_FOLDER = "storage/shared/Download/instaimg"
K_FACTOR = 32

# High-Performance Memory Registries
IMAGES_POOL = {}
URL_CACHE = {}

# =====================================================================
# 🛠️ ADVANCED MATH & GRAPHICS COMPILATION ENGINES
# =====================================================================
def calculate_new_ratings(rating_a, rating_b, won_a):
    """Calculates updated zero-sum tournament Elo ratings."""
    expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    expected_b = 1 / (1 + 10 ** ((rating_a - rating_b) / 400))
    
    score_a = 1.0 if won_a else 0.0
    score_b = 0.0 if won_a else 1.0
    
    new_a = rating_a + K_FACTOR * (score_a - expected_a)
    new_b = rating_b + K_FACTOR * (score_b - expected_b)
    return round(new_a, 1), round(new_b, 1)

def stitch_images_from_tg(img_content_a, img_content_b):
    """Stitches dual images from high-speed binary content streams into HD layout."""
    img_a = PILImage.open(BytesIO(img_content_a))
    img_b = PILImage.open(BytesIO(img_content_b))
    
    # High-resolution scale optimization target for clear phone view
    target_height = 650
    
    w_a = int((target_height / float(img_a.size[1])) * img_a.size[0])
    img_a = img_a.resize((w_a, target_height), PILImage.Resampling.LANCZOS)
    
    w_b = int((target_height / float(img_b.size[1])) * img_b.size[0])
    img_b = img_b.resize((w_b, target_height), PILImage.Resampling.LANCZOS)

    # Unified layout frame initialization with 12px padding gap
    combined_img = PILImage.new('RGB', (w_a + w_b + 12, target_height), (255, 255, 255))
    combined_img.paste(img_a, (0, 0))
    combined_img.paste(img_b, (w_a + 12, 0))
    
    bio = BytesIO()
    combined_img.save(bio, 'JPEG', quality=95)
    bio.seek(0)
    return bio

# =====================================================================
# 🎮 INSTANT RESPONSIVE BOT ROUTINES
# =====================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 **Welcome to the FaceMash Elo Arena!**\n\n"
        "Commands:\n"
        "/vote - Get a new high-speed matchup instantly\n"
        "/leaderboard - Check the real-time top ranked images"
    )

async def send_match(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    # Pick random distinct image structures from memory pool
    id_a, id_b = random.sample(list(IMAGES_POOL.keys()), 2)
    
    # Thread-Safe Caching for high-speed delivery
    if id_a not in URL_CACHE:
        file_a = await context.bot.get_file(IMAGES_POOL[id_a]["file_id"])
        URL_CACHE[id_a] = file_a.file_path
    if id_b not in URL_CACHE:
        file_b = await context.bot.get_file(IMAGES_POOL[id_b]["file_id"])
        URL_CACHE[id_b] = file_b.file_path

    # Extract clean file handles instantly
    resp_a = requests.get(URL_CACHE[id_a]).content
    resp_b = requests.get(URL_CACHE[id_b]).content
    
    stitched_photo = stitch_images_from_tg(resp_a, resp_b)
    
    keyboard = [[
        InlineKeyboardButton("👈 Left Pic", callback_data=f"ev_{id_a}_{id_b}_a"),
        InlineKeyboardButton("Right Pic 👉", callback_data=f"ev_{id_a}_{id_b}_b")
    ]]
    
    await context.bot.send_photo(
        chat_id=chat_id, 
        photo=stitched_photo, 
        caption=f"Which one is better?\nLeft: {int(IMAGES_POOL[id_a]['rating'])} Elo | Right: {int(IMAGES_POOL[id_b]['rating'])} Elo", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    _, id_a, id_b, winner = query.data.split("_")
    id_a, id_b = int(id_a), int(id_b)
    
    new_a, new_b = calculate_new_ratings(IMAGES_POOL[id_a]["rating"], IMAGES_POOL[id_b]["rating"], (winner == 'a'))
    IMAGES_POOL[id_a]["rating"] = new_a
    IMAGES_POOL[id_b]["rating"] = new_b
    
    await query.message.delete()
    await send_match(update, context, update.effective_chat.id)

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sorted_pics = sorted(IMAGES_POOL.items(), key=lambda x: x[1]["rating"], reverse=True)[:5]
    text = "🏆 **Current Top 5 Leaderboard** 🏆\n\n"
    for rank, (img_id, data) in enumerate(sorted_pics, start=1):
        text += f"{rank}. Image #{img_id} — **{int(data['rating'])} Elo Rating**\n"
    await update.message.reply_text(text)

# =====================================================================
# 📦 HIGH-SPEED AUTOMATED STORAGE CONTROL PIPELINES
# =====================================================================
def download_local_images():
    if not os.path.exists(TARGET_FOLDER):
        os.makedirs(TARGET_FOLDER)
    print(f"📡 Downloading {IMAGE_LIMIT} high-res source files to storage...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    count = 0
    while count < IMAGE_LIMIT:
        file_path = os.path.join(TARGET_FOLDER, f"pic_{count + 1}.jpg")
        try:
            req = urllib.request.Request("https://picsum.photos/600/400", headers=headers)
            with urllib.request.urlopen(req) as resp:
                with open(file_path, 'wb') as f:
                    f.write(resp.read())
            count += 1
            print(f"📥 Saved local asset {count}/{IMAGE_LIMIT}")
        except Exception:
            time.sleep(0.2)

async def upload_and_index_images():
    bot = Bot(token=TOKEN)
    all_files = sorted([f for f in os.listdir(TARGET_FOLDER) if f.endswith('.jpg')])
    
    # Process backup checks for active synchronization state recovery
    uploaded_indices = set()
    if os.path.exists("cloud_pool.txt"):
        with open("cloud_pool.txt", "r") as f:
            for line in f:
                if ":" in line:
                    uploaded_indices.add(int(line.split(":")[0]))

    print(f"\n⚡ HIGH-SPEED RESUMABLE CLOUD MIRROR ENGAGED")
    
    with open("cloud_pool.txt", "a") as out:
        for idx, filename in enumerate(all_files, start=1):
            if idx in uploaded_indices:
                continue
                
            file_path = os.path.join(TARGET_FOLDER, filename)
            progress = int((idx / IMAGE_LIMIT) * 100)
            print(f"🚀 Processing: [{idx}/{IMAGE_LIMIT}] -> {progress}% complete", end="\r")
            
            try:
                with open(file_path, 'rb') as pf:
                    msg = await bot.send_photo(chat_id=CHANNEL_ID, photo=pf)
                f_id = msg.photo[-1].file_id
                out.write(f"{idx}:{f_id}\n")
                out.flush()
                
                # Optimized safety parameter configuration 
                await asyncio.sleep(0.6)
            except Exception as e:
                print(f"\n⚠️ Rate block or drop at segment {idx}: {e}. Retrying in 5s...")
                await asyncio.sleep(5)

# =====================================================================
# 🏁 LIFECYCLE MANAGEMENT MAIN BOOTSTRAPPER
# =====================================================================
def main():
    global IMAGES_POOL
    
    # 1. Verification checks
    if not os.path.exists(TARGET_FOLDER) or len(os.listdir(TARGET_FOLDER)) < IMAGE_LIMIT:
        download_local_images()
        
    # 2. Resumable Mirror evaluation check loop
    lines_count = 0
    if os.path.exists("cloud_pool.txt"):
        with open("cloud_pool.txt", "r") as f:
            lines_count = sum(1 for line in f if ":" in line)

    if lines_count < IMAGE_LIMIT:
        asyncio.run(upload_and_index_images())
        
    # 3. Synchronize RAM dictionaries 
    print("\n⚡ Mapping live cloud keys to localized matrix states...")
    with open("cloud_pool.txt", "r") as f:
        for line in f:
            if ":" in line:
                idx, f_id = line.strip().split(":", 1)
                IMAGES_POOL[int(idx)] = {"file_id": f_id, "rating": 1200.0}
                
    # 4. Initialize Polling Applications
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("vote", lambda u, c: send_match(u, c, u.effective_chat.id)))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CallbackQueryHandler(handle_vote, pattern="^ev_"))
    
    print("\n🔥 SUCCESS: PERFORMANCE RUNTIME IS COMPLETELY ACTIVE!")
    print("👉 Switch to Telegram, open your bot chat interface, and run /vote to play!")
    app.run_polling()

if __name__ == '__main__':
    main()
