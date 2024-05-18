import asyncio
import aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


async def main():
    tokens = await get_tokens()
    loop = asyncio.get_event_loop()
    dispatchers = []
    for token in tokens:
        bot = Bot(token=token)
        dp = Dispatcher(bot)
        dp.register_message_handler(lambda message, bot=bot: start_handler(message, bot, token), commands=['start'])
        dp.register_message_handler(lambda message, bot=bot: webapp_handler(message, bot, token), commands=['webapp'])
        dispatchers.append(dp)
        loop.create_task(dp.start_polling())
    await asyncio.gather(*[dp.wait_closed() for dp in dispatchers])


async def get_tokens():
    tokens = []
    async with aiosqlite.connect('bot_tokens.db') as conn:
        async with conn.execute("SELECT token FROM bot_tokens") as cursor:
            async for row in cursor:
                tokens.append(row[0])
    return tokens


async def start_handler(message: types.Message, bot: Bot, token: str):
    user_profile_photos = await bot.get_user_profile_photos(message.from_user.id, limit=1)
    if user_profile_photos.total_count > 0:
        photo = user_profile_photos.photos[0][-1]
        file_id = photo.file_id
        file_path = await bot.get_file(file_id)
        avatar_url = f'https://api.telegram.org/file/bot{token}/{file_path.file_path}'
    else:
        avatar_url = ''

    # Store the avatar URL in the user's data (you can use a database or in-memory store)
    user_data[message.from_user.id] = {'avatar_url': avatar_url}

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text="Новости", url="https://t.me/jasonbot_news"),
        InlineKeyboardButton(text="Поддержка", url="https://t.me/Jsupport_bot"),
        InlineKeyboardButton(text="Чат", url="https://t.me/jasonbot_chat")
    )
    await bot.send_message(chat_id=message.from_user.id,
                           text="<b>Привет!</b>\n"
                                "<b>Спасибо за доверие!</b>\n\n"
                                "@jasonbot_news\n"
                                "(https://t.me/jasonbot_news).\n"
                                "новостной канал - здесь мы публикуем информацию об "
                                "обновлениях, выкладываем полезные материалы и "
                                "рассказываем об акциях\n\n"
                                "@jasonbot_chat\n"
                                "(https://t.me/jasonbot_chat)-\n"
                                "чат, где вы можете задать вопрос по работе бота, "
                                "внести свои предложения, рассказать чего вам не "
                                "хватает, чтобы автоматизировать работу с каналом",
                           parse_mode='html',
                           reply_markup=keyboard)


async def webapp_handler(message: types.Message, bot: Bot, token: str):
    avatar_url = user_data.get(message.from_user.id, {}).get('avatar_url', '')
    web_app_url = f"https://andreyka239.github.io/bot_v6/?avatar_url={avatar_url}"

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    webapp_button = KeyboardButton(text="Open Telegram Web App",
                                   web_app=types.WebAppInfo(url=web_app_url))
    keyboard.add(webapp_button)
    await bot.send_message(chat_id=message.from_user.id,
                           text='Нажмите кнопку ниже, чтобы открыть Telegram Web App.',
                           reply_markup=keyboard)


if __name__ == '__main__':
    user_data = {}  # In-memory store for user data, replace with a database in production
    asyncio.run(main())
