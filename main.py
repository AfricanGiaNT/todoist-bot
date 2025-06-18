import os
import asyncio
import logging
from http import HTTPStatus
from flask import Flask, request, Response
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler
from telegram_bot.handlers import start, help_command, add_task_handler, complete_task_handler

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Set up the Telegram bot application
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Add command handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("add", add_task_handler))
application.add_handler(CommandHandler("complete", complete_task_handler))

# Set up the Flask app
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook() -> Response:
    """Handle incoming Telegram updates."""
    logger.info("Webhook received.")
    # Run the async function in a new event loop
    asyncio.run(process_update(request.get_json(force=True)))
    return Response(status=HTTPStatus.OK)

async def process_update(data: dict):
    """Process the incoming update from Telegram."""
    await application.initialize()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    await application.shutdown()

if __name__ == '__main__':
    logger.info("Starting bot...")
    extra_files = ['config/projects.json']
    app.run(debug=True, host='0.0.0.0', port=5002, extra_files=extra_files) 