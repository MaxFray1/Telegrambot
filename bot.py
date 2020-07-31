from aiogram.utils.markdown import text
import parcer
import config
import asyncio
import datetime
import logging
import database

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ContentType

API_TOKEN = config.TOKEN

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

button_check = InlineKeyboardButton("Проверить все статьи", callback_data="button_check")
button_add = InlineKeyboardButton("Добавить ссылку", callback_data="button_add")
button_edit = InlineKeyboardButton("Редактировать ссылку", callback_data="button_edit")
button_delete = InlineKeyboardButton("Удалить ссылку", callback_data="button_delete")
button_back = InlineKeyboardButton("Назад", callback_data="button_back")
button_deleteAll = InlineKeyboardButton("Удалить все ВАШИ ссылки", callback_data="button_deleteAll")

button_addUser = InlineKeyboardButton("Добавить пользователя", callback_data="button_addUser")
button_deleteUser = InlineKeyboardButton("Удалить пользователя", callback_data="button_deleteUser")
button_editUser = InlineKeyboardButton("Изменить пользователя", callback_data="button_editUser")

markup_main = InlineKeyboardMarkup()
markup_main.add(button_check)
markup_main.add(button_add)
# markup_main.add(button_edit)
markup_main.add(button_delete)
markup_main.add(button_deleteAll)

markup_back = InlineKeyboardMarkup()
markup_back.add(button_back)

markup_admin = InlineKeyboardMarkup()
markup_admin.add(button_addUser)
markup_admin.add(button_deleteUser)
markup_admin.add(button_back)

flags = [False, False, False, False, False, False]


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id, text="Привет!👋🏻 Я бот Ваня! Работающий с Дзен.\n"
                                                            "Я – бот, который отслеживает параметр noindex на твоих статьях в Яндекс Дзен.\n\n"
                                                            "Теперь я буду обновлять каждую минуту все твои статьи и моментально доложу, если появится noindex, чтобы ты смог вовремя удалить статью и не улететь в бан 👾\n\n"
                                                            "Я работаю полностью анонимно и без сбоев, 24 часа в сутки.\n\n"
                                                            "По всем вопросам можешь писать в тех. поддержку.")
    if await database.check_user(message.from_user.username) == None:
        await bot.send_message(chat_id=message.from_user.id, text="У тебя нет активной подписки на бота. Пожалуйста оформите подписку)")
        return
    await message.answer("Выберите что хотите сделать:", reply_markup=markup_main, parse_mode="html")


@dp.message_handler(commands=['PASSWORDtoADMIN'])
async def send_welcome(message: types.Message):
    if await database.check_admin(message.from_user.username) == None:
        await bot.send_message(chat_id=message.from_user.id, text="Нет прав(Этого сообщения не будет)")
        return
    await message.answer("АДМИН ПАНЕЛЬ", reply_markup=markup_admin, parse_mode="html")


@dp.message_handler()
async def echo(message: types.Message):
    if await database.check_user(message.from_user.username) == None:
        await bot.send_message(chat_id=message.from_user.id, text="Пожалуйста оформите подписку)")
        return
    if not (str(message.text).find("zen.yandex.ru/media/id/") == -1) and flags[0]:
        count = await database.increase_count(message.from_user.username)
        if not count == 0:
            await database.insert_link(message.text, message.from_user.id)
            flags[0] = False
            await bot.send_message(chat_id=message.from_user.id, text="Статья добавлена у вас осталось "+str(count)+" статей")
        else:
            await bot.send_message(chat_id=message.from_user.id, text="Ваш лимит статей исчерпан! Пожалуйста улучшите вашу подписку")
    elif not (str(message.text).find("zen.yandex.ru/media/id/") == -1) and flags[1]:
        flags[1] = False
        print("test!!!")
    elif not (str(message.text).find("zen.yandex.ru/media/id/") == -1) and flags[2]:
        await database.decrease_count(message.from_user.username)
        await database.delete_link(message.text)
        flags[2] = False
        await bot.send_message(chat_id=message.from_user.id, text="Статья удалена")
    elif message.text == "Удалить все статьи" and flags[3]:
        await database.delete_all_link(message.from_user.id)
        flags[3] = False
        await bot.send_message(chat_id=message.from_user.id, text="Все ваши статьи удалены")
    elif not (str(message.text).find("Добавить(") == -1) and flags[4]:
        await add_user(message.text)
        flags[4] = False
        await bot.send_message(chat_id=message.from_user.id, text="Пользователь добавлен")
    elif not (str(message.text).find("Удалить(") == -1) and flags[5]:
        await delete_user(message.text)
        print("testDelete")
        flags[5] = False
        await bot.send_message(chat_id=message.from_user.id, text="Пользователь удалён")
    else:
        await bot.send_message(chat_id=message.from_user.id, text="Возможно вы где-то ошиблись, повторите действие снова или обратитесь в тех.поддержку")
    await message.answer("Выберите что хотите сделать: ", reply_markup=markup_main, parse_mode="html")


@dp.callback_query_handler(text="button_check")
async def process_callback_check(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    for i in database.show_links(callback_query.from_user.id):
        await bot.send_message(chat_id=callback_query.from_user.id, text=i)


@dp.callback_query_handler(text="button_add")
async def process_callback_check(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    flags[0] = True
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, text="Отправьте ссылку на статью, чтобы добавить её в базу для проверки", reply_markup=markup_back)


@dp.callback_query_handler(text="button_edit")
async def process_callback_check(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    flags[1] = True
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, text="ПОКА НЕ РАБОТАЕТ Отправьте сообщение в формате: url - 1/0\nГде url - это ссылка на статью, а 1 - проверять, 0 - не проверять", reply_markup=markup_back)


@dp.callback_query_handler(text="button_delete")
async def process_callback_check(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    flags[2] = True
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, text="Отправьте ссылку на статью, чтобы удалить статью из базы на проверку", reply_markup=markup_back)


@dp.callback_query_handler(text="button_back")
async def process_callback_check(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(text="Выберите что хотите сделать: ", chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, reply_markup=markup_main, parse_mode="html")


@dp.callback_query_handler(text="button_deleteAll")
async def process_callback_check(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    flags[3] = True
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, text='Отправьте сообщение "Удалить все статьи" для подтверждения действия', reply_markup=markup_back)


@dp.callback_query_handler(text="button_addUser")
async def process_callback_check(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    if await database.check_user(callback_query.from_user.id) == None:
        await bot.send_message(chat_id=callback_query.from_user.id, text="Пожалуйста оформите подписку)")
        return
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                text="Чтобы добавить пользователя введите следующие данные\n"
                                "Добавить(Имя_пользователя, привелегии, количество_дней, количество_статей)\n"
                                "Обязательное разделение между параметрами одна запятая! Привелегии (0-админ, 1-пользователь)\n"
                                "Количество дней и статей (-1 если без ограничения)\n"
                                "Пример: Добавить(username, 1, 30, 5)",
                                reply_markup=markup_back)
    flags[4] = True


@dp.callback_query_handler(text="button_deleteUser")
async def process_callback_check(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    if await database.check_user(callback_query.from_user.id) == None:
        await bot.send_message(chat_id=callback_query.from_user.id, text="Пожалуйста оформите подписку)")
        return
    print("testDeleteButton")
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                text='Чтобы удалить пользователя введите следующие данные\n"Удалить(Имя пользователя)"',
                                reply_markup=markup_back)
    flags[5] = True


# unknown message
@dp.message_handler(content_types=ContentType.ANY)
async def unknown_message(msg: types.Message):
    message_text = text("Я не знаю, что с этим делать.\nНапоминаю, что есть команда /help")
    await msg.reply(ContentType)


async def scheduled():
    while True:
        await asyncio.sleep(config.Timer1)
        for row in database.check_links():
            print(row[0])
            if parcer.check(row[0]):
                await bot.send_message(chat_id=row[1], text="NOINDEX\n"+row[0])
                await database.delete_link(row[0])
        await asyncio.sleep(config.Timer2)


async def add_user(text):
    text = text.replace(' ', '')
    text = text.replace('Добавить(', '')
    text = text[:-1]
    data = text.split(',')
    await database.insert_user(data[0], 13, "dateReg", data[1], data[2], data[3])


async def delete_user(text):
    text = text.replace(' ', '')
    text = text.replace('Добавить(', '')
    text = text[:-1]
    await database.delete_user(text)
    print('teeest')


def addAdmins():
    for i in config.admins:
        database.insert_user2(i[0],i[1], 'dateReg', i[2], i[3], i[4])


async def scheduled():
    while True:
        
        await asyncio.sleep(86400)


if __name__ == '__main__':
    addAdmins()
    dp.loop.create_task(scheduled())
    executor.start_polling(dp, skip_updates=True)

