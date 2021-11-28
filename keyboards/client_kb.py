from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Файл с клавиатурами
cancelButton = KeyboardButton("Отмена")

machinesMenu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
m1 = KeyboardButton('Атлант')
m2 = KeyboardButton('Вертикальная')
machinesMenu.add(m1, m2).add(cancelButton)

dateMenu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
todayButton = KeyboardButton("Сегодня")
tomorrowButton = KeyboardButton("Завтра")
dateMenu.add(todayButton, tomorrowButton).add(cancelButton)

clientMenu = ReplyKeyboardMarkup(resize_keyboard=True)
bookButton = KeyboardButton("/note")
helpButton = KeyboardButton("/help")
showListButton = KeyboardButton("/list")
clientMenu.add(bookButton, helpButton).add(showListButton)

cancel_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
cancel_menu.add(cancelButton)

submitMenu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
submitButton = KeyboardButton("Верно")
submitMenu.add(submitButton)

# YOU CAN COMBINE THESE METHODS