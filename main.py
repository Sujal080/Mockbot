import os
import asyncio
import threading
import logging
from flask import Flask
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

# Validate configuration
if not TOKEN or TOKEN == 'your_bot_token_here':
    raise ValueError("Invalid Telegram token in .env file")
if not ADMIN_CHAT_ID:
    raise ValueError("Missing ADMIN_CHAT_ID in .env file")

# Global bot reference
bot_application = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logger.info(f"Received start command from {update.effective_chat.id}")
        
        if str(update.effective_chat.id) != ADMIN_CHAT_ID:
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        await update.message.reply_text(
            "🤖 TestBook Bot Activated!\n\n"
            "Send me a TestBook test series URL to begin."
        )
        logger.info("Start command processed successfully")
    except Exception as e:
        logger.error(f"Start command failed: {e}")

def create_bot_application():
    """Create and configure the bot application"""
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    return application

async def run_bot():
    """Run the bot with proper async handling"""
    global bot_application
    try:
        logger.info("Initializing bot application...")
        bot_application = create_bot_application()
        
        logger.info("Starting bot polling...")
        await bot_application.initialize()
        await bot_application.start()
        await bot_application.updater.start_polling()
        
        logger.info("Bot is now running")
        while True:
            await asyncio.sleep(3600)  # Run indefinitely
            
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
    finally:
        if bot_application:
            await bot_application.stop()
            await bot_application.shutdown()

def run_flask():
    """Run the Flask web server"""
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting Flask on port {port}")
    app.run(host='0.0.0.0', port=port)

@app.route('/')
def home():
    return {"status": "running", "bot_active": bool(bot_application)}, 200

@app.route('/ping')
def ping():
    return "pong", 200

def start_bot():
    """Start the bot in a new event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot())

if __name__ == '__main__':
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    # Start Flask server in main thread
    run_flask()