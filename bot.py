import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# ================== LOAD ENV ==================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing!")

# ================== LOGGING ==================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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

# ================== BUILD APPLICATION ==================
application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))

# ================== RUN ==================
if __name__ == "__main__":
    # Detect if running on Render
    is_render = os.getenv("RENDER") == "true" or "RENDER_EXTERNAL_HOSTNAME" in os.environ

    if is_render:
        # ========== WEBHOOK MODE (Render) ==========
        from fastapi import FastAPI, Request, HTTPException
        import uvicorn

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await application.initialize()
            await application.start()

            domain = os.getenv("RENDER_EXTERNAL_HOSTNAME")
            if domain:
                webhook_url = f"https://{domain}/webhook"
                await application.bot.set_webhook(url=webhook_url)
                logger.info(f"Webhook set to: {webhook_url}")
            else:
                logger.warning("RENDER_EXTERNAL_HOSTNAME not found")

            yield

            await application.stop()
            await application.shutdown()

        app = FastAPI(lifespan=lifespan)

        @app.post("/webhook")
        async def webhook(request: Request):
            if request.headers.get("content-type") == "application/json":
                data = await request.json()
                update = Update.de_json(data, application.bot)
                await application.process_update(update)
                return {"ok": True}
            raise HTTPException(status_code=400, detail="Invalid content-type")

        @app.get("/")
        async def health():
            return {"status": "Based Alpha Only bot is running ✅"}

        port = int(os.getenv("PORT", 10000))
        uvicorn.run(app, host="0.0.0.0", port=port)

    else:
        # ========== POLLING MODE (Local) ==========
        logger.info("Running in polling mode...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
