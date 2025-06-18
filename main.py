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
PORT = int(os.environ.get('PORT', 8000))
HOST_URL = os.environ.get('HOST_URL')

# Set up the Telegram bot application
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Add command handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("add", add_task_handler))
application.add_handler(CommandHandler("complete", complete_task_handler))

# Set up the Flask app
app = Flask(__name__)

@app.before_request
async def initialize_bot():
    """Initialize the bot before handling a request."""
    await application.initialize()
    if not HOST_URL:
        raise ValueError("HOST_URL environment variable not set.")
    webhook_info = await application.bot.get_webhook_info()
    webhook_url = f"{HOST_URL}/webhook"
    if webhook_info.url != webhook_url:
        await application.bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook set to {webhook_url}")

@app.route('/webhook', methods=['POST'])
async def webhook() -> Response:
    """Handle incoming Telegram updates."""
    try:
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, application.bot)
        await application.process_update(update)
        return Response(status=HTTPStatus.OK)
    except Exception as e:
        logger.error(f"Error processing update: {e}", exc_info=True)
        return Response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

@app.route('/')
def index():
    """A simple endpoint to confirm the server is running."""
    return "Bot is running!"

if __name__ == '__main__':
    # This block is for local development and won't be used by a production server like Gunicorn.
    # For production, Gunicorn or another WSGI/ASGI server will import the `app` object.
    logger.info(f"Starting bot locally on port {PORT}...")
    app.run(debug=True, host='0.0.0.0', port=PORT) 