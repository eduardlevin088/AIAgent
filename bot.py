import asyncio
import logging
import uuid
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from config import BOT_TOKEN, SUPERADMIN_ID
from services.agent import generate_response
from services.new_conv import new_conversation
from services.miscellaneous import format_repair_text_minimal as format_message
from database import init_db, close_db, create_or_update_user
from database import get_user_session, get_admin_ids
from database import create_admin, delete_admin


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    # Save/update user in database
    user = message.from_user
    conversation_id = new_conversation()

    await create_or_update_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        session_id=conversation_id
    )

    response, data_to_send = generate_response('Здравствуйте', conversation_id)
    
    await message.answer(response)




@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """
Available commands:
/start - Start / Restart the bot
/help - Show this help message
/about - About the bot
    """
    await message.answer(help_text)


@dp.message(Command("about"))
async def cmd_about(message: Message):
    await message.answer(
        "This is a Telegram bot built with aiogram 3.x\n"
        "Bot is ready to be customized!"
    )


@dp.message(Command("newadmin"))
async def add_admin(message: Message):
    if message.from_user.id == SUPERADMIN_ID:
        new_admin_id = int(message.text.split()[1])
        print(new_admin_id)
        await create_admin(
            user_id=new_admin_id
        )

        await message.answer(f"Admin id {new_admin_id} added")
    else:
        await message.answer("Insufficient rights")


@dp.message(Command("admin"))
async def req_admin(message: Message):
    await bot.send_message(SUPERADMIN_ID, f"Admin request {message.from_user.id}")

    await message.answer("Request sent")


@dp.message()
async def echo_handler(message: Message):
    print("\n\n\n\n\n\n\n\n\n12321347628760487098\n\n\n\n\n\n\n")
    user = message.from_user
    session_id = await get_user_session(user.id)
    response, data_to_send = generate_response(message.text, session_id)
    
    await message.answer(response)

    if data_to_send:
        admin_ids = await get_admin_ids()
        for admin_id in admin_ids:
            await bot.send_message(
                admin_id, 
                format_message(data_to_send)
            )


async def main():

    logger.info("Starting bot...")
    try:
        await init_db()
        
        await bot.delete_webhook(drop_pending_updates=True)
        
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error occurred: {e}")
    finally:
        await close_db()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

