import asyncio
import logging
import uuid
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from config import BOT_TOKEN, ADMIN_IDS
from services.langflow import agent_response
from database import init_db, close_db, create_or_update_user
from database import save_message, get_user_session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command"""
    # Save/update user in database
    user = message.from_user
    await create_or_update_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        session_id=str(uuid.uuid4())
    )
    
    await message.answer(
        f"Hello, {user.first_name}! 👋\n\n"
        "Welcome to the bot! Use /help to see available commands. \n\n(latest commit: initial .github/workflows/deploy.yml setup)"
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command"""
    help_text = """
Available commands:
/start - Start the bot
/help - Show this help message
/about - About the bot
    """
    await message.answer(help_text)


@dp.message(Command("about"))
async def cmd_about(message: Message):
    """Handle /about command"""
    await message.answer(
        "This is a Telegram bot built with aiogram 3.x\n"
        "Bot is ready to be customized!"
    )


@dp.message()
async def echo_handler(message: Message):
    """Echo handler for all other messages"""
    # Save message to database
    user = message.from_user
    await save_message(user_id=user.id, message_text=message.text or "")
    
    session_id = await get_user_session(user.id)

    response = agent_response(message.text, session_id)
    
    await message.answer(response)


async def main():
    """Main function to run the bot"""
    logger.info("Starting bot...")
    try:
        # Initialize database
        await init_db()
        
        # Delete webhook if exists
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Start polling
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error occurred: {e}")
    finally:
        # Close database connection
        await close_db()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

