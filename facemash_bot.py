import os
import sys
import time
import random
import asyncio
import urllib.request
import json  # 💾 Integrated for persistent data structures
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
DB_FILE = "database.json"  # Local JSON storage file matrix
K_FACTOR = 32

IMAGES_POOL = {}
URL_CACHE = {}

# =====================================================================
# 💾 ADVANCED DATABASE CONTROLS
# =====================================================================
def load_database():
    """Restores tournament history records directly from disk database layer."""
    global IMAGES_POOL
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                saved_scores = json.load(f)
                for img_id, score in saved_scores.items():
                    if int(img_id) in IMAGES_POOL:
                        IMAGES_POOL[int(img_id)]["rating"] = float(score)
            print("💾 Database Synced: Historical Elos restored successfully.")
        except Exception as e:
            print(f"⚠️ Database parsing variant skipped: {e}")

def save_database():
    """Flushes active state dynamic RAM ratings into persistent JSON array."""
    try:
        export_data = {str(k): v["rating"] for k, v in IMAGES_POOL.items()}
        with open(DB_FILE, "w") as f:
            json.dump(export_data, f, indent=4)
    except Exception as e:
        print(f"❌ Database commit transaction failed: {e}")

# =====================================================================
# 🛠️ ADVANCED MATH & GRAPHICS COMPILATION ENGINES
# =====================================================================
def calculate_new_ratings(rating_a, rating_b, won_a):
    expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    expected_b = 1 / (1 + 10 ** ((rating_a - rating_b) / 400))
    score_a = 1.0 if won_a else 0.0
    score_b = 0.0 if won_a else 1.0
    new_a = rating_a + K_FACTOR * (score_a - expected_a)
    new_b = rating_b + K_FACTOR * (score_b - expected_b)
    return round(new_a, 1), round(new_b, 1)

def stitch_images_from_tg(img_content_a, img_content_b):
    img_a = PILImage.open(BytesIO(img_content_a))
    img_b = PILImage.open(BytesIO(img_content_b))
    
    target_height = 650
    w_a = int((target_height / float(img_a.size[1])) * img_a.size[0])
    img_a = img_a.resize((w_a, target_height), PILImage.Resampling.LANCZOS)
    
    w_b = int((target_height / float(img_b.size[1])) * img_b.size[0])
    img_b = img_b.resize((w_b, target_height), PILImage.Resampling.LANCZOS)

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
        "/vote - Get a new high-speed matchup frame\n"
        "/leaderboard - Check top ranked images\n"
        "/reset - Wipe tournament matrix back to base 1200"
    )

async def send_match(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    id_a, id_b = random.sample(list(IMAGES_POOL.keys()), 2)
    
    if id_a not in URL_CACHE:
        file_a = await context.bot.get_file(IMAGES_POOL[id_a]["file_id"])
        URL_CACHE[id_a] = file_a.file_path
    if id_b not in URL_CACHE:
        file_b = await context.bot.get_file(IMAGES_POOL[id_b]["file_id"])
        URL_CACHE[id_b] = file_b.file_path

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
    
    save_database()  # Commit updates directly to disk database tracking
    await query.message.delete()
    await send_match(update, context, update.effective_chat.id)

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sorted_pics = sorted(IMAGES_POOL.items(), key=lambda x: x[1]["rating"], reverse=True)[:5]
    text = "🏆 **Current Top 5 Leaderboard** 🏆\n\n"
    for rank, (img_id, data) in enumerate(sorted_pics, start=1):
        text += f"{rank}. Image #{img_id} — **{int(data['rating'])} Elo Rating**\n"
    await update.message.reply_text(text)

async def reset_tournament(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wipes out database logs and restores tournament history arrays."""
    for img_id in IMAGES_POOL:
        IMAGES_POOL[img_id]["rating"] = 1200.0
    save_database()
    await update.message.reply_text("🔄 **Tournament Reset Complete!** All assets returned to base 1200 Elo.")

# =====================================================================
# 📦 CLOUD STORAGE MIRROR PIPELINES
# =====================================================================
def download_local_images():
    if not os.path.exists(TARGET_FOLDER):
        os.makedirs(TARGET_FOLDER)
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
        except Exception:
            time.sleep(0.1)

async def upload_and_index_images():
    bot = Bot(token=TOKEN)
    all_files = sorted([f for f in os.listdir(TARGET_FOLDER) if f.endswith('.jpg')])
    
    uploaded_indices = set()
    if os.path.exists("cloud_pool.txt"):
        with open("cloud_pool.txt", "r") as f:
            for line in f:
                if ":" in line:
                    uploaded_indices.add(int(line.split(":")[0]))

    with open("cloud_pool.txt", "a") as out:
        for idx, filename in enumerate(all_files, start=1):
            if idx in uploaded_indices:
                continue
            file_path = os.path.join(TARGET_FOLDER, filename)
            try:
                with open(file_path, 'rb') as pf:
                    msg = await bot.send_photo(chat_id=CHANNEL_ID, photo=pf)
                f_id = msg.photo[-1].file_id
                out.write(f"{idx}:{f_id}\n")
                out.flush()
                await asyncio.sleep(0.6)
            except Exception:
                await asyncio.sleep(5)

# =====================================================================
# 🏁 LIFECYCLE INITIALIZER BOOTSTRAPPER
# =====================================================================
def main():
    global IMAGES_POOL
    
    if not os.path.exists(TARGET_FOLDER) or len(os.listdir(TARGET_FOLDER)) < IMAGE_LIMIT:
        download_local_images()
        
    lines_count = 0
    if os.path.exists("cloud_pool.txt"):
        with open("cloud_pool.txt", "r") as f:
            lines_count = sum(1 for line in f if ":" in line)

    if lines_count < IMAGE_LIMIT:
        asyncio.run(upload_and_index_images())
        
    with open("cloud_pool.txt", "r") as f:
        for line in f:
            if ":" in line:
                idx, f_id = line.strip().split(":", 1)
                IMAGES_POOL[int(idx)] = {"file_id": f_id, "rating": 1200.0}
                
    load_database()  # Recover existing Elo configuration states if file exists
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("vote", lambda u, c: send_match(u, c, u.effective_chat.id)))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CommandHandler("reset", reset_tournament))
    app.add_handler(CallbackQueryHandler(handle_vote, pattern="^ev_"))
    
    print("\n🔥 PERFORMANCE RUNTIME IS COMPLETELY ACTIVE!")
    app.run_polling()

if __name__ == '__main__':
    main()
