import os
import logging
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# ================== CONFIG ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Will be your Render URL + /webhook

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing!")

# ================== LOGGING ==================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================== FASTAPI APP ==================
app = FastAPI()

# Create the Telegram Application
telegram_app = Application.builder().token(BOT_TOKEN).build()

# ================== /start HANDLER ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    welcome_text = f"""
🚀 **Welcome to Based Alpha Only**

Hey {user.first_name}!

For support, please DM → **@pixe1eth**

---

💎 **Become a Premium Member**

Get full access to the private group + premium bot features.

**Available Plans:**
• 1 Month  → **$50**
• 3 Months → **$120**
• 6 Months → **$250**

---

💳 **How to Pay & Join**

1. Choose a plan  
2. Send the exact amount using one of the payment methods below  
3. After payment, send the **transaction hash / screenshot** to **@pixe1eth**  
4. You will be added to the private group and get premium access

**Payment Options:**
• USDT (TRC20): `YOUR_TRC20_ADDRESS`
• USDT (ERC20 / BEP20): `YOUR_ERC20_ADDRESS`
• BTC: `YOUR_BTC_ADDRESS`
• SOL: `YOUR_SOL_ADDRESS`
• Other methods → Ask @pixe1eth

Once payment is confirmed, you’ll receive the private group link + premium access.
"""

    keyboard = [
        [InlineKeyboardButton("📩 Contact Support", url="https://t.me/pixe1eth")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

    # Notify Admin
    if ADMIN_CHAT_ID:
        admin_text = (
            f"🆕 **New user started the bot!**\n\n"
            f"Name: {user.full_name}\n"
            f"Username: @{user.username if user.username else 'None'}\n"
            f"User ID: `{user.id}`\n"
            f"Chat ID: `{chat_id}`"
        )
        try:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=admin_text,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to notify admin: {e}")

# Register the handler
telegram_app.add_handler(CommandHandler("start", start))

# ================== WEBHOOK ENDPOINT ==================
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}

@app.get("/")
async def home():
    return {"status": "Based Alpha Only bot is running"}

# ================== STARTUP ==================
@app.on_event("startup")
async def startup():
    await telegram_app.initialize()
    await telegram_app.start()
    
    if WEBHOOK_URL:
        await telegram_app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
        logger.info(f"Webhook set to {WEBHOOK_URL}/webhook")
    else:
        logger.warning("WEBHOOK_URL not set!")
