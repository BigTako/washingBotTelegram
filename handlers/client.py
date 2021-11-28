import string
from aiogram import types, Dispatcher
from loader import bot
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from database import database as db
import datetime as dt
from logger import log_func, logger
from keyboards.client_kb import clientMenu, machinesMenu, cancel_menu, dateMenu, submitMenu

__group_id = -1001608774061 # id группы для отсылки записей

def validate_data(date: str, char:str):
    """Функия исправления введенного времени или даты. Параметры:
       date--> дата или время в виде строки  char--> обозначение("d"-->дата "t"-->время)"""
    if char == "d": # если в ф-ию передали дату
        for s in date:
            if s in string.punctuation:
                date = date.replace(s, "/") # заменить промежуточные символы бэкслешем

        currentYear = str(dt.datetime.now().year) # текущий год в формате строки
        day, month = str(date.split("/")[0]), str(date.split("/")[1]) # выделить введенные день и месяц
        return day + "/" + month + "/" + currentYear # определить новую дату

    elif char == "t": # если в ф-ию передали время
        for s in date:
            if s in string.punctuation:
                date = date.replace(s, ":")
                # заменить промежуточные символы двоеточием
        if len(date) < 3: # если ввели часы без минут
            date += ":00"
        return date

class FSMclient(StatesGroup): # класс машины состояний
    #start anketing
    username = State()
    machine = State()
    date_from = State()
    start = State()
    date_to = State()
    finish = State()

@log_func
async def command_start(message: types.Message):
    """Функция вывода приветсвия и/или списка команд"""
    try :
        msg = "Привет!Я бот для записи чата стралок🤖\n" \
                  "Вот список всез доступных команд: \n" \
                  "Команды: /start или /help\n" \
                  "Сделать запись:/note\n" \
                  "Просмотреть записи:/list\n" \
                  "Отменить заполнение: Отмена или отмена\n" \
                  "Техподдержка:/baddev\n" \
                  "Предложка:/gooddev\n"
        await bot.send_message(message.from_user.id, msg, reply_markup=clientMenu)
        await message.delete()
    except:
        await message.reply("Вы не писали боту ранее😯\n"
                            "Самое время это сделать👆")

@log_func
async def cm_start(message: types.Message):
    """Начальная ф-ия машины состояний"""
    await FSMclient.machine.set()
    await message.reply("Какую машинку занимаете?🤔", reply_markup=machinesMenu)

async def set_machine(message: types.Message, state: FSMContext):
    logger.info(f"User called {set_machine.__name__}")
    try:
        async with state.proxy() as data:
            if message.from_user.username == None: # Если имя пользователя скрыто
                data["username"] = message.from_user.first_name
            else:
                data["username"] = "@" + str(message.from_user.username)

            if message.text == "Атлант" or message.text == "Вертикальная":
                data['machine'] = str(message.text)  # записать название машинки в словать данных
                await FSMclient.next()  # wait for answer for next question
                await message.answer("Укажите дату начала📅\nКастомно->Любой формат", reply_markup=dateMenu)
            else:
                await message.reply("Неверное название машинки‼️\nПопробуйте снова: ♻")
    except Exception as ex:
        # если ошибка
        logger.error(f"User-{message.from_user.first_name} - Function: {set_date_from.__name__}.\n"
                     f"Arguments: {message, state}\nError: {ex}")
        await message.reply("Ошибка.Напишите 'отмена' и попробуйте снова.", reply_markup=cancel_menu)

async def set_date_from(message: types.Message, state: FSMContext):
    """Функция задания даты начала стирки"""
    logger.info(f"User called {set_date_from.__name__}")
    today = dt.datetime.today() # сегодня в формате datetime
    tomorrow = today + dt.timedelta(days=1) # завтра в формате datetime
    try:
        async with state.proxy() as data:
            if message.text == "Сегодня":
                data["datestart"] = dt.datetime.strftime(today, "%d/%m/%Y")
            elif message.text == "Завтра":
                data["datestart"] = dt.datetime.strftime(tomorrow, "%d/%m/%Y")
            else:
                # ввод кастомной даты
                data["datestart"] = validate_data(message.text, "d")
                date_start = dt.datetime.strptime(validate_data(message.text, "d"), "%d/%m/%Y")
                tms1 = int(dt.datetime.timestamp(today))  # сегодня в формате таймстемп
                tms2 = int(dt.datetime.timestamp(date_start))  # введенная дата в формате таймстемп
                if tms2 < tms1:
                    # Если таймстемп введенной даты меньше сегодняшней
                    raise Exception

            await FSMclient.next()
            await message.answer("Укажите время начала(любой формат): ",reply_markup=cancel_menu)

    except Exception as ex:
        # если дата была введена неверно или возникла ошибка
        await message.reply("Неверный формат даты!Попробуйте снова\n"
                            "Или нажмите 'отмена' для выхода", reply_markup=dateMenu)
        logger.error(f"User-{message.from_user.first_name} - Function: {set_date_from.__name__}.\n"
                     f"Arguments: {message, state}\nError: {ex}")


async def set_time_from(message: types.Message, state: FSMContext):
    """Функция задания начального времени"""
    logger.info(f"User called {set_date_from.__name__}")
    msg = "⚠️Неверный формат времени!"
    try:
        async with state.proxy() as data:
            time = dt.datetime.strptime(validate_data(message.text,"t"), "%H:%M")
            #Если время введено невероно, выдаст исключение

            if not db.check_time_itersection(validate_data(message.text,"t"), data["datestart"], "s"):
                # Проверяет занято ли время.Если да --> вернет False
                msg = "⚠️Это время уже занято!"
                raise Exception

            data['start'] = validate_data(message.text, "t")
            await message.reply("Введите дату завершения📅\nКастомно->Любой формат ", reply_markup=dateMenu)
            await FSMclient.next()
    except Exception as ex:
        await message.reply(f"{msg}Попробуйте снова\n"
                            "Или нажмите 'отмена' для выхода",reply_markup=cancel_menu)
        logger.error(f"Function: {set_date_from.__name__}.\nArguments: {message, state}\nError: {ex}")

async def set_date_to(message: types.Message, state: FSMContext):
    """Фунцкия задания конечной даты"""
    logger.info(f"User called {set_date_from.__name__}")
    today = dt.datetime.today()
    tomorrow = today + dt.timedelta(days=1)
    msg = "Неверный формат даты!"
    try:
        async with state.proxy() as data:
            if message.text == "Сегодня":
                data["datefinish"] = dt.datetime.strftime(today, "%d/%m/%Y")
            elif message.text == "Завтра":
                data["datefinish"] = dt.datetime.strftime(tomorrow, "%d/%m/%Y")
            else:
                #check date block
                data["datefinish"] = validate_data(message.text, "d")

            date_finish = dt.datetime.strptime(validate_data(data["datefinish"], "d"), "%d/%m/%Y")
            # проверяет правильность ввода даты. Если нет --> вернет исключение
            tms1 = int(dt.datetime.timestamp(dt.datetime.strptime(data["datestart"], "%d/%m/%Y"))) #таймстемп даты завершения
            tms2 = int(dt.datetime.timestamp(date_finish))  # таймстемп даты завершения
            if tms1 > tms2:
                msg = "Дата завершения не может быть раньше начала!"
                raise Exception

            await FSMclient.next()
            await message.answer("Укажите время завершения: ", reply_markup=cancel_menu)

    except Exception as ex:
        await message.reply(f"⚠️{msg}Попробуйте снова\n"
                            "Или нажмите 'отмена' для выхода", reply_markup=dateMenu)
        logger.error(f"User-{message.from_user.first_name} - Function: {set_date_from.__name__}.\n"
                     f"Arguments: {message, state}\nError: {ex}")


async def set_time_to(message: types.Message, state: FSMContext):
    """Функция задания конечного времени"""
    logger.info(f"User called {set_date_from.__name__}")
    msg = "⚠️Неверный формат времени!"
    try:
        async with state.proxy() as data:
            time = dt.datetime.strptime(validate_data(message.text,"t"), "%H:%M")
            # Проверяет правильность ввода времени
            data['finish'] = validate_data(message.text, "t")

            # таймстемп даты начала
            tms1 = int(dt.datetime.timestamp(dt.datetime.strptime(data["datestart"], "%d/%m/%Y")))
            # таймстемп даты завершения
            tms2 = int(dt.datetime.timestamp(dt.datetime.strptime(data["datefinish"], "%d/%m/%Y")))
            times = int(dt.datetime.timestamp(
                dt.datetime.strptime(data["datestart"] + " " + data["start"], "%d/%m/%Y %H:%M")))
            # таймстемп времени начала
            timef = int(dt.datetime.timestamp(
                dt.datetime.strptime(data["datefinish"] + " " + data["finish"], "%d/%m/%Y %H:%M")))
            # таймстемп времени завершения стрирки

            if tms2 == tms1 and times >= timef:
                msg = "⚠️Время одинаковое или мешьше начального!"
                raise Exception
            if timef - times > 10800: # more than 3 hours
                msg = "⚠️Нельзя занимать более 3-х часов!"
                raise Exception
            if not db.check_time_itersection(validate_data(message.text,"t"), data["datefinish"], "f"):
                msg = "⚠️Это время уже занято!"
                raise Exception

            await message.reply(f"Вы ввели такие данные:\n"
                                f"Машинка: {data['machine']}\n"
                                f"Начало : {data['datestart']} {data['start']}\n"
                                f"Завершение: {data['datefinish']} {data['finish']}\n")
            await message.answer("Если данные верны, нажмите 'Верно'\n"
                                 "Если нет, нажмите /note и повторите запись.", reply_markup=submitMenu)
            await FSMclient.next()
    except Exception as ex:
        print(ex)
        await message.reply(f"{msg} Попробуйте снова.\nИли нажмите 'отмена' для выхода")
        logger.error(f"User-{message.from_user.first_name} - Function: {set_date_from.__name__}.\n"
                     f"Arguments: {message, state}\nError: {ex}")


async def submit(message:types.Message, state: FSMContext):
    """Функция подтверждения введеных данных"""
    logger.info(f"User called {set_date_from.__name__}")
    try:
        async with state.proxy() as data:
            username = data["username"]
            machine = data["machine"]
            date_s = data["datestart"]
            date_f = data["datefinish"]
            time_s = data["start"]
            time_f = data["finish"]

            time_start = dt.datetime.timestamp(dt.datetime.strptime(f"{date_s} {time_s}", "%d/%m/%Y %H:%M"))
            # Перевести дату и время начала вместе из строки в таймстемп
            time_finish = dt.datetime.timestamp(dt.datetime.strptime(f"{date_f} {time_f}", "%d/%m/%Y %H:%M"))
            # Перевести дату и время завершения вместе из строки в таймстемп
            db.write_to_db((username, machine, time_start, time_finish))

            msg = f"⬛️Пользователь: {data['username']}\n" \
                  f"🟣Машинка: {data['machine']}\n" \
                  f"🟣С : {data['datestart']} {data['start']}\n" \
                  f"⬛️По: {data['datefinish']} {data['finish']}\n" \

            await message.answer("Данные успешно приняты!✅", reply_markup=clientMenu)
            await bot.send_message(__group_id, msg)
            await state.finish()
    except Exception as ex:
        await message.reply("⚠️Пожалуйста, выберите один\n"
                            "из вариантов выше.")
        logger.error(f"User-{message.from_user.first_name} - Function: {set_date_from.__name__}.\n"
                     f"Arguments: {message, state}\nError: {ex}")

async def get_notes(message:types.Message):
    """Функция получения всех записей"""
    logger.info(f"User called {set_date_from.__name__}")
    try:
        notes = db.read_data_from_db()
        if len(notes) == 0:
            await message.reply("Записи не обнаружены📋")
        else:
            for note in notes:
                num = notes.index(note)
                time_from = dt.datetime.strftime(dt.datetime.fromtimestamp(int(note[3])), "%d/%m/%Y %H:%M")
                time_to = dt.datetime.strftime(dt.datetime.fromtimestamp(int(note[4])), "%d/%m/%Y %H:%M")
                msg = f"{num + 1})👾Пользователь: {note[1]}\n" \
                      f"🟣Машинка: {note[2]}\n" \
                      f"🟣C: {time_from}\n" \
                      f"🟣По: {time_to}\n"
                await message.answer(msg)

    except Exception as ex:
        await message.reply("Пожалуйста, выберите один\n"
                    "из вариантов выше.")
        logger.error(f"User-{message.from_user.first_name} - Function: {set_date_from.__name__}.\n"
                f"Arguments: {message}\nError: {ex}")


async def cancel_handler(message: types.Message, state: FSMContext):
    """Функция отмены анкетирования машины состояний"""
    current_state = await state.get_state()
    if current_state is None:
        await message.reply("Вы не делаете запись в данный момент.", reply_markup=clientMenu)
        return
    await message.reply("Заполнение отменено👌",reply_markup=clientMenu)
    await state.finish()

async def delete_old_notices(message:types.Message):
    """Функция удаления прошедших записей"""
    logger.info(f"User called {set_date_from.__name__}")
    try:
        db.delete_old()
        await message.reply("Удаление успешно завершено!",reply_markup=clientMenu)
    except Exception as ex:
        await message.reply("Удаление не завершено!",reply_markup=clientMenu)
        logger.error(f"User-{message.from_user.first_name} - Function: {set_date_from.__name__}.\n"
                     f"Arguments: {message}\nError: {ex}")

async def kick_developer(message:types.Message):
    """Функция контакта с разработчиком"""
    await message.answer("Тг разработчика: @abibsosay\n"
                         "Не сильно его там🤕")

async def send_log_file(message:types.Message):
    """Функция отправки файла логирования"""
    with open("logs.log", 'rb', encoding="utf-8") as file:
        await bot.send_document(message.chat.id, file)

async def empty_handler(message:types.Message):
    """Пустой хендлер"""
    await message.reply("Бот не понял, что Вы написали😑")

@log_func
def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'help'])
    dp.register_message_handler(cancel_handler, Text(equals='Отмена', ignore_case=True), state="*")
    dp.register_message_handler(cm_start, commands=["note"],state=None)
    dp.register_message_handler(get_notes, commands=["list"])
    dp.register_message_handler(kick_developer, commands=["baddev", "gooddev"])
    dp.register_message_handler(send_log_file, commands=["sendlogfile"])
    dp.register_message_handler(set_machine, state=FSMclient.machine)
    dp.register_message_handler(set_date_from, state=FSMclient.date_from)
    dp.register_message_handler(set_time_from, state=FSMclient.start)
    dp.register_message_handler(set_date_to, state=FSMclient.date_to)
    dp.register_message_handler(set_time_to, state=FSMclient.finish)
    dp.register_message_handler(submit, Text(equals="Верно", ignore_case=True), state="*")
    dp.register_message_handler(delete_old_notices, commands=["deleteoldnoticesadmin"])
    dp.register_message_handler(empty_handler)
