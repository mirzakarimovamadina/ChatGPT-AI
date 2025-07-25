import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram.methods import DeleteWebhook
from aiogram.client.session.aiohttp import AiohttpSession

from config import BOT_TOKEN
from services.mistral_service import get_mistral_reply
from utils.history import update_chat_history, clear_user_history, chat_history, user_last_activity


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


session = AiohttpSession()
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML, session=session)
dp = Dispatcher()


@dp.message(CommandStart())
async def handle_start(message: Message):
    user_last_activity[message.from_user.id] = datetime.now()
    await message.answer(
        "👋 <b>Keling tanishib olaylik!</b>\n\n"
        "🤖 Men sizning AI yordamchingizman. Quyidagilarni qila olaman:\n"
        "➤ Matnli savollaringizga javob beraman\n"
        "➤ Har qanday mavzuda izoh, yechim yoki maslahat bera olaman\n\n"
        "✍️ Savolingizni yozing men sizga javob berishga harakat qilaman. Boshladikmi?"
    )


@dp.message(Command("clear"))
async def handle_clear(message: Message):
    user_last_activity[message.from_user.id] = datetime.now()
    clear_user_history(message.chat.id)
    await message.answer("💬 Suhbat tarixi tozalandi!")


@dp.message(F.text & ~F.text.startswith("/"))
async def handle_text(message: Message):
    if len(message.text) > 1000:
        return

    user_id = message.from_user.id
    chat_id = message.chat.id
    user_last_activity[user_id] = datetime.now()

    loading = await message.answer("🧠 <b>Savolingiz tahlil qilinmoqda...</b>")

    try:
        update_chat_history(chat_id, message.text)
        reply = await get_mistral_reply(chat_id, message.text)
        update_chat_history(chat_id, reply, role="assistant")

        await bot.delete_message(chat_id, loading.message_id)
        await message.answer(reply, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"[Xatolik] {e}")
        try:
            await bot.delete_message(chat_id, loading.message_id)
        except:
            pass
        await message.answer("❌ Xatolik yuz berdi. Keyinroq urinib ko‘ring.")


async def notify_inactive_users():
    while True:
        await asyncio.sleep(3600)
        week_ago = datetime.now() - timedelta(days=7)

        for user_id, last_active in list(user_last_activity.items()):
            if last_active <= week_ago:
                try:
                    await bot.send_message(
                        user_id,
                        "👀 Men seni ko‘rmayapman, nega yordam so‘ramayapsan?\nYordam kerak bo‘lsa bemalol yoz 😉"
                    )
                    user_last_activity[user_id] = datetime.now()
                except Exception as e:
                    logger.warning(f"{user_id} ga yuborilmadi: {e}")
                    user_last_activity.pop(user_id, None)


async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    asyncio.create_task(notify_inactive_users())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
