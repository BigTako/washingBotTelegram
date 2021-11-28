from aiogram.utils import executor
from loader import dp
from handlers import client
from database.database import connect_to_db
async def on_startup(_):
    print("Bot went online!")
    connect_to_db()

# ...************************CLIENT PART*********************...
client.register_handlers_client(dp)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
