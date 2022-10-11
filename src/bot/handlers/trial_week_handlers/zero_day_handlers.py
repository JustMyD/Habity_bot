from ...init_bot import dp, INIT_DAY_FUNCTIONS
from ...const.msgs import DAY_0_INTRO_MSG, DAY_0_MSG_1, DAY_0_MSG_2, USER_GOAL_MSG_1, USER_GOAL_MSG_2, USER_GOAL_MSG_3, DAY_0_MSG_3

import json
from typing import Union

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMStateGoal(StatesGroup):
    state_first_message = State()
    state_second_message = State()
    state_third_message = State()
    state_fourth_message = State()


# @dp.message_handler(commands='start')
async def intro_message(message: Union[types.Message, str]):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text='Определить цель'))
    user_data = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    if isinstance(message, types.Message):
        user_id = message.from_user.id
    elif isinstance(message, str):
        user_id = message
    if user_id not in user_data.keys():
        user_data[user_id] = {
            "Обращение": "",
            "Цель": "",
            "Срок цели": "",
            "Зачем цель": "",
            "Привычки": [],
            "Установки": [],
            "Напоминать об установках": "",
            "Характеристики": [],
            "Время отправки сообщений": "",
            "Текущий пробный день": "0",
            "Был оповещен сегодня": "Нет",
        }
        json.dump(user_data, open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'w'), ensure_ascii=False, indent=3)
    if isinstance(message, types.Message):
        await message.answer(text=DAY_0_INTRO_MSG)
        await message.answer(text=DAY_0_MSG_1, reply_markup=keyboard)
    elif isinstance(message, str):
        await bot.send_message(chat_id=user_id, text=DAY_0_INTRO_MSG)
        await bot.send_message(chat_id=user_id, text=DAY_0_MSG_1, reply_markup=keyboard)


# @dp.message_handler(Text('Определить цель'), state=None)
async def start_get_user_goal(message: types.Message):
    await FSMStateGoal.state_first_message.set()
    await message.answer(text=USER_GOAL_MSG_1, reply_markup=types.ReplyKeyboardRemove())


# @dp.message_handler(state=FSMStateGoal.state_third_message)
async def get_user_goal_reason(message: types.Message, state: FSMContext):
    await FSMStateGoal.state_fourth_message.set()
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Утром')],
        [types.KeyboardButton(text='Днем')],
        [types.KeyboardButton(text='Вечером')]
    ], resize_keyboard=True)
    async with state.proxy() as data:
        data['Зачем цель'] = message.text
    await message.answer(text=DAY_0_MSG_2, reply_markup=keyboard)


# @dp.message_handler(Text(['Утром', 'Днем', 'Вечером']), state=FSMStateGoal.state_fourth_message)
async def zeroday_last_message(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    chat_id = message.chat.id
    user_preferences = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    if str(user_id) not in user_preferences.keys():
        user_preferences[user_id] = {}
    async with state.proxy() as data:
        user_preferences[user_id]['Цель'] = data['Цель']
        user_preferences[user_id]['Срок цели'] = data['Срок цели']
        user_preferences[user_id]['Зачем цель'] = data['Зачем цель']
    user_preferences[user_id]['Время отправки сообщений'] = message.text
    user_preferences[user_id]['Текущий пробный день'] = '1'
    user_preferences[user_id]['Был оповещен сегодня'] = 'Да'
    json.dump(user_preferences, open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'w'),
              ensure_ascii=False, indent=3)
    await message.answer(text=DAY_0_MSG_3, reply_markup=types.ReplyKeyboardRemove())


def register_handlers_zero_day(dp: Dispatcher):
    dp.register_message_handler(intro_message, commands='start')
    dp.register_message_handler(start_get_user_goal, Text('Определить цель'), state=None)
    dp.register_message_handler(get_user_goal_reason, state=FSMStateGoal.state_third_message)
    dp.register_message_handler(zeroday_last_message, Text(['Утром', 'Днем', 'Вечером']),  state=FSMStateGoal.state_fourth_message)

INIT_DAY_FUNCTIONS.update({'0': intro_message})