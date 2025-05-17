import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from testbook_scraper import TestBookScraper
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

async def start(update: Update, context):
    if str(update.effective_chat.id) != ADMIN_CHAT_ID:
        await update.message.reply_text("Unauthorized access.")
        return
    
    await update.message.reply_text(
        "📚 TestBook Mock Test Scraper Bot\n\n"
        "Send me a TestBook test series URL (e.g., https://testbook.com/ssc-cgl/test-series)\n\n"
        "I'll extract mock tests and send them in HTML format with timer functionality."
    )

async def handle_url(update: Update, context):
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

async def handle_timer(update: Update, context):
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
        logger.error(f"Error scraping mock tests: {e}")
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"❌ Error scraping mock tests: {str(e)}"
        )

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    application.add_handler(CallbackQueryHandler(handle_timer))
    
    application.run_polling()

if __name__ == '__main__':
    main()