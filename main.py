import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from testbook_scraper import TestBookScraper
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

def start(update: Update, context: CallbackContext):
    if str(update.effective_chat.id) != ADMIN_CHAT_ID:
        update.message.reply_text("Unauthorized access.")
        return
    
    update.message.reply_text(
        "📚 TestBook Mock Test Scraper Bot\n\n"
        "Send me a TestBook test series URL (e.g., https://testbook.com/ssc-cgl/test-series)\n\n"
        "I'll extract mock tests and send them in HTML format with timer functionality."
    )

def handle_url(update: Update, context: CallbackContext):
    if str(update.effective_chat.id) != ADMIN_CHAT_ID:
        return
    
    url = update.message.text
    if not url.startswith('https://testbook.com/') or '/test-series' not in url:
        update.message.reply_text("Please send a valid TestBook test series URL.")
        return
    
    update.message.reply_text(
        "⏱ Please select test duration:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("30 mins", callback_data=f"timer_30_{url}")],
            [InlineKeyboardButton("60 mins", callback_data=f"timer_60_{url}")],
            [InlineKeyboardButton("90 mins", callback_data=f"timer_90_{url}")],
            [InlineKeyboardButton("120 mins", callback_data=f"timer_120_{url}")]
        ])
    )

def handle_timer(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    if str(query.message.chat_id) != ADMIN_CHAT_ID:
        return
    
    data = query.data.split('_')
    minutes = int(data[1])
    url = '_'.join(data[2:])
    
    query.edit_message_text(f"⏳ Scraping mock tests from {url} with {minutes} minute timer...")
    
    try:
        scraper = TestBookScraper()
        mocks = scraper.scrape_test_series(url, minutes)
        
        if not mocks:
            context.bot.send_message(
                chat_id=query.message.chat_id,
                text="❌ No mock tests found on this page. Try a different URL."
            )
            return
            
        for mock in mocks:
            with open(mock['html_file'], 'rb') as f:
                context.bot.send_document(
                    chat_id=query.message.chat_id,
                    document=f,
                    filename=f"mock_test_{mock['id']}.html",
                    caption=f"🧠 {mock['title']}\n⏱ Timer: {minutes} minutes"
                )
    except Exception as e:
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"❌ Error scraping mock tests: {str(e)}"
        )

def error(update: Update, context: CallbackContext):
    print(f"Update {update} caused error {context.error}")

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_url))
    dp.add_handler(CallbackQueryHandler(handle_timer, pattern='^timer_'))
    dp.add_error_handler(error)
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()