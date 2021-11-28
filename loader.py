from aiogram import Bot, Dispatcher
from config import API_TOKEN
from aiogram.contrib.fsm_storage.memory import MemoryStorage
#  can keep data in RAM ^

storage = MemoryStorage()

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

