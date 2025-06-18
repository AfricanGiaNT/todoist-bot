import os
import asyncio
import logging
from telegram import Update
from telegram.ext import ContextTypes
from todoist.api import create_task, find_task_by_content, complete_task
from config.loader import load_project_mappings, find_project_section

logger = logging.getLogger(__name__)

TODOIST_API_TOKEN = os.getenv("TODOIST_API_TOKEN")
PROJECT_MAPPINGS = load_project_mappings()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_html(
        "Welcome to the Todoist Bot! Add tasks by sending a message. Use /help for more commands."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with the list of available commands."""
    await update.message.reply_text(
        "Available commands:\n"
        "/add <task> - Add a new task\n"
        "/complete <task> - Complete a task\n"
        "/help - Show this help message"
    )

async def add_task_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Adds a new task to Todoist, automatically categorizing it."""
    full_message = " ".join(context.args)
    logger.info(f"Received /add command with content: '{full_message}'")

    if not full_message:
        await update.message.reply_text("Please provide a task to add. Usage: /add <task> - <category hint>")
        return

    # Parse the message for task content and category hint
    if " - " in full_message:
        parts = full_message.split(" - ", 1)
        task_content = parts[0].strip()
        category_hint = parts[1].strip()
    else:
        task_content = full_message
        category_hint = full_message

    logger.info(f"Task Content: '{task_content}', Category Hint: '{category_hint}'")

    try:
        # Find project and section from the hint
        project_name, section_name = find_project_section(category_hint, PROJECT_MAPPINGS)
        logger.info(f"Mapped to Project: '{project_name}', Section: '{section_name}'")

        # Running synchronous function in a separate thread
        task = await asyncio.to_thread(
            create_task,
            TODOIST_API_TOKEN,
            task_content,
            project_name=project_name,
            section_name=section_name
        )
        if task:
            logger.info(f"Task '{task.content}' created successfully in Todoist.")
            await update.message.reply_text(f"Task '{task.content}' added successfully!")
        else:
            logger.error("Failed to create task in Todoist.")
            await update.message.reply_text("Failed to add task.")
    except Exception as e:
        logger.error(f"Error in add_task_handler: {e}", exc_info=True)
        await update.message.reply_text(f"An error occurred: {e}")

async def complete_task_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Completes a task in Todoist."""
    task_content = " ".join(context.args)
    logger.info(f"Received /complete command with content: '{task_content}'")
    if not task_content:
        await update.message.reply_text("Please provide a task to complete. Usage: /complete <task>")
        return

    try:
        # Running synchronous functions in a separate thread
        task = await asyncio.to_thread(find_task_by_content, TODOIST_API_TOKEN, task_content)
        if task:
            logger.info(f"Found task '{task.content}' to complete.")
            success = await asyncio.to_thread(complete_task, TODOIST_API_TOKEN, task.id)
            if success:
                logger.info(f"Task '{task.content}' completed successfully.")
                await update.message.reply_text(f"Task '{task.content}' completed!")
            else:
                logger.error(f"Failed to complete task '{task.content}'.")
                await update.message.reply_text(f"Failed to complete task '{task.content}'.")
        else:
            logger.warning(f"Task '{task_content}' not found for completion.")
            await update.message.reply_text(f"Task '{task_content}' not found.")
    except Exception as e:
        logger.error(f"Error in complete_task_handler: {e}", exc_info=True)
        await update.message.reply_text(f"An error occurred: {e}") 