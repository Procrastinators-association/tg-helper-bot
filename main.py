import asyncio
import os
import sqlite3
import tempfile

import aiogram

bot = aiogram.Bot(token='5573020445:AAFMWLw17H0k8IpMjGn616fFDVPM0-P82KQ', parse_mode='HTML')

db = sqlite3.connect('main.db')
db.execute('''
create table if not exists task (
    id integer primary key autoincrement,
    user_id integer,
    file_id text,
    status text
)''')
db.commit()


# Статус бывает: AWAITING_PROCESSING, AWAITING_NOTIFICATION, DONE


async def notify(text, user: int, bot: aiogram.Bot):
    await bot.send_chat_action(chat_id=user, action='typing')
    await asyncio.sleep(5)
    await bot.send_message(chat_id=user, text=text)


async def calc_picture_size(message: aiogram.types.Message):
    photo = message.photo[-1]
    file_path = os.path.join(tempfile.gettempdir(), 'pic_' + photo.file_unique_id)
    await photo.download(destination_file=file_path)
    connection = db.cursor()
    connection.execute('insert into task (user_id, file_id, status) values (?, ?, ?)',
                       [message.chat.id, photo.file_unique_id, 'AWAITING_NOTIFICATION'])
    db.commit()
    asyncio.create_task(notify(f'Ваш чек обработан {photo.file_unique_id}. Приходите ещё.', message.chat.id, bot))
    await message.answer(f'Размер картинки {message.photo[-1].file_size} 😆')


async def handle_notifications():
    while True:
        print('Я работаю')
        connection = db.cursor()
        connection.execute(
            "select id, user_id, file_id from task where status = 'AWAITING_NOTIFICATION' order by id limit 1"
        )
        task = connection.fetchone()
        if task:
            id, user_id, file_id = task
            await bot.send_message(chat_id=user_id, text=file_id)
            connection.execute("update task set status = 'DONE' where id = ?", [id])
            db.commit()
        await asyncio.sleep(2)


async def handle_accountant(message: aiogram.types.Message):
    if message.text == 'Я бухгалтер':
        await message.answer('Наконец-то! Вот ваш <strike>небо</strike>свод.')


def main():
    dispatcher = aiogram.Dispatcher(bot)
    dispatcher.register_message_handler(calc_picture_size, content_types=aiogram.types.ContentType.PHOTO)
    dispatcher.register_message_handler(handle_accountant, content_types=aiogram.types.ContentType.TEXT)
    aiogram.executor.start_polling(
        dispatcher=dispatcher,
        skip_updates=True
    )


if __name__ == '__main__':
    main()
    # asyncio.run(handle_notifications())
