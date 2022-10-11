from aiogram import executor
from bot.init_bot import dp
from bot.handlers import setup_dispatcher_handlers


if __name__ == '__main__':
    setup_dispatcher_handlers(dp)

    executor.start_polling(dp, skip_updates=True)
