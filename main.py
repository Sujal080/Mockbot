import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
from testbook_scraper import TestBookScraper
from dotenv import load_dotenv

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

# Validate token
if not TOKEN or TOKEN == 'your_bot_token_here':
    raise ValueError("Invalid Telegram token. Please set TELEGRAM_BOT_TOKEN in .env file")

# Telegram Bot Handlers (same as before)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != ADMIN_CHAT_ID:
        await update.message.reply_text("Unauthorized access.")
        return
    
    await update.message.reply_text(
        "📚 TestBook Mock Test Scraper Bot\n\n"
        "Send me a TestBook test series URL (e.g., https://testbook.com/ssc-cgl/test-series)\n\n"
        "I'll extract mock tests and send them in HTML format with timer functionality."
    )

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != ADMIN_CHAT_ID:
        return
    
    url = update.message.text
    if not url.startswith('https://testbook.com/') or '/test-series' not in url:
        await update.message.reply_text("Please send a valid TestBook test series URL.")
        return
    
    keyboard = [
        [
            InlineKeyboardButton("30 mins", callback_data=f"30|{url}"),
            InlineKeyboardButton("60 mins", callback_data=f"60|{url}"),
        ],
        [
            InlineKeyboardButton("90 mins", callback_data=f"90|{url}"),
            InlineKeyboardButton("120 mins", callback_data=f"120|{url}"),
        ]
    ]
    
    await update.message.reply_text(
        "⏱ Please select test duration:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if str(query.message.chat_id) != ADMIN_CHAT_ID:
        return
    
    minutes, url = query.data.split('|')
    minutes = int(minutes)
    
    await query.edit_message_text(f"⏳ Scraping mock tests from {url} with {minutes} minute timer...")
    
    try:
        scraper = TestBookScraper()
        mocks = scraper.scrape_test_series(url, minutes)
        
        if not mocks:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="❌ No mock tests found on this page. Try a different URL."
            )
            return
            
        for mock in mocks:
            with open(mock['html_file'], 'rb') as f:
                await context.bot.send_document(
                    chat_id=query.message.chat_id,
                    document=f,
                    filename=f"mock_test_{mock['id']}.html",
                    caption=f"🧠 {mock['title']}\n⏱ Timer: {minutes} minutes"
                )
    except Exception as e:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"❌ Error scraping mock tests: {str(e)}"
        )

# Flask Routes
@app.route('/')
def home():
    return "TestBook Bot is running", 200

@app.route('/health')
def health():
    return {"status": "ok", "bot": "active"}, 200

def run_bot():
    """Run the Telegram bot in polling mode"""
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    application.add_handler(CallbackQueryHandler(handle_timer))
    
    application.run_polling()

if __name__ == '__main__':
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Start Flask server
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)