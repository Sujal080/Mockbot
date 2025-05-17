import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Initialize logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

# Validate token
if not TOKEN or TOKEN == 'your_bot_token_here':
    raise ValueError("Invalid Telegram token. Please set TELEGRAM_BOT_TOKEN in .env file")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="TestBook Bot is running!"
    )

def main():
    try:
        application = ApplicationBuilder().token(TOKEN).build()
        
        application.add_handler(CommandHandler("start", start))
        
        logger.info("Starting bot...")
        application.run_polling()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    main()