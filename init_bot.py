import os

from aiogram import Bot, Dispatcher, types


bot = Bot(token=os.getenv('API_TOKEN'))
dp = Dispatcher(bot)


@dp.message_handler(commands='start')
async def greetings(message: types.Message):
    await message.answer(text=message.text)
