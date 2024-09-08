import asyncio
import time

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import requests

import config



# Объект бота
bot = Bot(token=config.BOT_API_TOKEN)
# Диспетчер
dp = Dispatcher()


@dp.message(Command("log", "лог"))
async def cmd_log(message: types.Message):
    await bot.send_message(message.chat.id, f"{message.chat.id}", disable_web_page_preview=True)
    # Узнаем ид пользователя.
    user_id = message.from_user.id
    # Данный функционал доступен только админам.
    if user_id in config.admins:
        import parser
        lst = parser.get_html("west")
        for i in lst:
            # print(i)
            time.sleep(config.delay_msg)
            await bot.send_message(message.chat.id, i, disable_web_page_preview=True)



def start_parser():
    print(f"start_parser")
    # asyncio.run(bot.send_message(-4583492531, "test"))
    import parser

    lst = parser.get_html("west")
    for i in lst:
        time.sleep(config.delay_msg)
        asyncio.run(bot.send_message(config.chat_id_for_fast, i))

    lst = parser.get_html("north")
    for i in lst:
        time.sleep(config.delay_msg)
        asyncio.run(bot.send_message(config.chat_id_for_fast, i))

    if len(lst) == 0:
        asyncio.run(bot.send_message(config.chat_id_for_fast,
                                     "Новых нет. Тестовая проверка. Просто проверка что бот не помер."))



def main():
    # await dp.start_polling(bot)
    start_parser()
    while True:
        time.sleep(config.delay)
        start_parser()


if __name__ == "__main__":
    main()
    # asyncio.run(main())
    # parser.get_html("west")
