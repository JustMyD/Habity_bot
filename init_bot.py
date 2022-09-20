import json
import os

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text, Regexp

from bot_messages import DAY_0_MSG_1, DAY_0_MSG_2, USER_GOAL_MSG

bot = Bot(token=os.getenv('API_TOKEN'))
dp = Dispatcher(bot)


@dp.message_handler(commands='start')
async def day_0_start_msg(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text='Отправить цель'))
    await message.answer(text=DAY_0_MSG_1, reply_markup=keyboard)


@dp.message_handler(Text('Отправить цель'))
async def get_user_goal(message: types.Message):
    await message.answer(text=USER_GOAL_MSG)


@dp.message_handler(Text('Название цели'))
async def get_user_time(message: types.Message):
    await message.answer(text=DAY_0_MSG_2)


@dp.message_handler(Regexp(r'\d+:\d+'))
async def day_0_end_msg(message: types.Message):
    user_id = message.from_user.id
    user_preferences = json.load(open('user_preferences.json', 'a'))
    user_data = user_preferences.get(user_id)
    if not user_data:
        user_preferences[user_id] = dict()
    user_preferences[user_id]['Отправить сообщение'] = message.text
    json.dump(user_preferences, open('user_preferences.json'))
    await message.answer(text='Отлично, мы с тобой определили цель, зачем она тебе и в какие сроки ты хочешь ее достичь. До завтра!')


# async def get_user_habits():
#     await bot.send_message(chat_id='', text='')
