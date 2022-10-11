from ...init_bot import dp, INIT_DAY_FUNCTIONS
from ...const.msgs import DAY_1_INTRO_MSG, DAY_1_MSG_1, USER_HABBIT_MSG_1, USER_HABBIT_MSG_2, USER_HABBIT_MSG_3, DAY_1_MSG_2

import json
import os
import time
from typing import Union

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

class FSMStateHabbit(StatesGroup):
    state_first_message = State()
    state_second_message = State()
    state_third_message = State()


# @dp.message_handler(Text('Начать первый день'))
async def first_day_intro(user_id: str):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text='Отправить привычку'))
    user_data = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    user_data[user_id]['Был оповещен сегодня'] = 'Да'
    json.dump(user_data, open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'w'), ensure_ascii=False, indent=3)
    await bot.send_message(chat_id=user_id, text=DAY_1_INTRO_MSG, reply_markup=types.ReplyKeyboardRemove())
    await bot.send_message(chat_id=user_id, text=DAY_1_MSG_1, reply_markup=keyboard)


# @dp.message_handler(Text(['Отправить привычку']), state=None)
async def get_user_habbit_name(message: types.Message):
    await FSMStateHabbit.state_first_message.set()
    await message.answer(text=USER_HABBIT_MSG_1, reply_markup=types.ReplyKeyboardRemove())


# @dp.message_handler(state=FSMStateHabbit.state_first_message)
async def get_user_habbit_trigger(message: types.Message, state: FSMContext):
    await FSMStateHabbit.state_second_message.set()
    async with state.proxy() as data:
        data['Название привычки'] = message.text
    await message.answer(text=USER_HABBIT_MSG_2)


# @dp.message_handler(state=FSMStateHabbit.state_second_message)
async def get_user_habbit_value(message: types.Message, state: FSMContext):
    await FSMStateHabbit.state_third_message.set()
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Да')],
        [types.KeyboardButton(text='Нет')]
    ], resize_keyboard=True)
    async with state.proxy() as data:
        data['Триггер привычки'] = message.text
    await message.answer(text=USER_HABBIT_MSG_3, reply_markup=keyboard)


@dp.message_handler(Text(['Да', 'Нет']), state=FSMStateHabbit.state_third_message)
async def first_day_last_message(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Отправить привычку')],
        [types.KeyboardButton(text='Изменить цель')]
    ])
    user_data = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    user_id = str(message.from_user.id)
    user_goal = user_data[user_id]['Цель']
    goal_date = user_data[user_id]['Срок цели']
    goal_reason = user_data[user_id]['Зачем цель']
    async with state.proxy() as data:
        new_habit = {
            'Название привычки': data['Название привычки'],
            'Триггер': data['Триггер привычки'],
            'Полезна?': message.text
        }
        user_data[user_id]['Привычки'].append(new_habit)
        user_data[user_id]['Текущий пробный день'] = '2'
        json.dump(user_data, open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'w'), ensure_ascii=False, indent=3)
    await message.answer(text=DAY_1_MSG_2.format(user_goal=user_goal, goal_date=goal_date, goal_reason=goal_reason),
                         reply_markup=keyboard)


def register_handlers_first_day(dp: Dispatcher):
    dp.register_message_handler(get_user_habbit_name, Text(['Отправить привычку']), state=None)
    dp.register_message_handler(get_user_habbit_trigger, state=FSMStateHabbit.state_first_message)
    dp.register_message_handler(get_user_habbit_value, state=FSMStateHabbit.state_second_message)
    dp.register_message_handler(first_day_last_message, Text(['Да', 'Нет']), state=FSMStateHabbit.state_third_message)

INIT_DAY_FUNCTIONS.update({'1': first_day_intro})
