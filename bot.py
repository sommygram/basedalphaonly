import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ================== CONFIG ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is missing!")

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

check our x for updates https://x.com/basedalphaonly
 
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
• USDT (TRC20): `TCNzzgw23nPce7TUiuNRzmVpBUfhbohAgc`
• USDT (ERC20 / BEP20): `0x65C243E4966E11772f85d3D3A121eeFDb0A8d99A`
• BTC: `bc1qv79mrckkr653gnf3jhal5lr8r5frcykqcf54mq`
• SOL: `tYmCTZ3rBU92xmYJB6WEAHSSGjrSZhSKyJuQq7Y6W94`
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

# ================== MAIN ==================
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
