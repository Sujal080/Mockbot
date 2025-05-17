# TestBook Mock Test Telegram Bot

This bot scrapes mock tests from TestBook URLs and sends them as HTML files with timers.

## Setup
1. Clone this repository
2. Create `.env` file from `.env.sample`
3. Install dependencies: `pip install -r requirements.txt`

## Deployment on Render
1. Create new Web Service
2. Connect GitHub repository
3. Set environment variables:
   - `TELEGRAM_BOT_TOKEN`
   - `ADMIN_CHAT_ID`
4. Deploy!

## Usage
1. Send a TestBook test series URL
2. Select timer duration
3. Receive downloadable HTML mock tests