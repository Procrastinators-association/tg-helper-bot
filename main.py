import tempfile

import aiogram
import aiohttp
import config

bot = aiogram.Bot(config.TOKEN, parse_mode='HTML')

dispatcher = aiogram.Dispatcher(bot)


async def calc(message: aiogram.types.Message):
    print(message.text)
    result = eval(message.text)
    await bot.send_message(chat_id=message.chat.id, text=str(result))


async def calc_picture_size(message: aiogram.types.Message):
    mktemp = tempfile.mktemp()
    print(await message.photo[-1].download(destination=mktemp))
    client = aiohttp.ClientSession()
    response = await client.post()
    payload = response.json()
    await message.answer(f'Размер картинки {message.photo[-1].file_size / 1024:.2} MB')


def main():
    dispatcher.register_message_handler(calc)
    dispatcher.register_message_handler(calc_picture_size, content_types=aiogram.types.ContentType.PHOTO)
    aiogram.executor.start_polling(
        dispatcher=dispatcher,
        skip_updates=True,
    )


if __name__ == '__main__':
    main()
