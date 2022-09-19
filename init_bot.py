import os

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text

from bot_messages import GREETING_MSG, USER_GOAL_MSG

bot = Bot(token=os.getenv('API_TOKEN'))
dp = Dispatcher(bot)


@dp.message_handler(commands='start')
async def greetings(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add(types.KeyboardButton(text='Отправить цель'))
    await message.answer(text=GREETING_MSG, reply_markup=keyboard)


@dp.message_handler(Text('Отправить цель'))
async def get_user_goal(message: types.Message):
    await message.answer(text=USER_GOAL_MSG)
