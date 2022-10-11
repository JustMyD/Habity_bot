"""
Пока все колбэки здесь в одной куче, нужно раскидать TrialDays функции по отдельным скриптам, в init скрипте
остаются основные колбэки
"""
from .const.msgs import MAIN_MENU_MSG
from .filters.custom_filters import NotCommand

import json
import os
import time
from typing import Union

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.callback_data import CallbackData
from dotenv import load_dotenv

load_dotenv()
INIT_DAY_FUNCTIONS = {}

bot = Bot(token=os.getenv('API_TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands='menu')
async def show_main_menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Моя цель')],
        [types.KeyboardButton(text='Мои привычки')],
        [types.KeyboardButton(text='Мои характеристики')],
        [types.KeyboardButton(text='Мои установки')],
        [types.KeyboardButton(text='Настройки')]
        ]
    )
    user_data = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    main_characteristic = user_data[str(message.from_user.id)]['Обращение']
    main_characteristic = main_characteristic if main_characteristic else 'Друг'
    await message.answer(text=MAIN_MENU_MSG.format(characteristic=main_characteristic), reply_markup=keyboard)


class FSMStateFeedback(StatesGroup):
    state_start_feedback = State()


@dp.message_handler(commands='feedback', state=None)
async def start_get_user_feedback(message: types.Message):
    await FSMStateFeedback.state_start_feedback.set()
    await message.answer(text='Напишите свой отзыв или пожелание')


@dp.message_handler(NotCommand(), state=FSMStateFeedback.state_start_feedback)
async def end_get_user_feedback(message: types.Message, state: FSMContext):
    feedback_group_id = '-1001868511126'
    await bot.forward_message(chat_id=feedback_group_id, from_chat_id=message.chat.id, message_id=message.message_id)
    await message.answer(text='Спасибо за ваши пожелания, мы их обязательно учтем')
    await state.finish()


# ToDo CallbackQuery для списка целей с возможностью изменения цели или ее удаления
@dp.message_handler(Text('Изменить цель'))
async def change_user_goal(query: types.CallbackQuery):
    pass


@dp.message_handler(Text('Удалить цель'))
async def delete_user_goal(query: types.CallbackQuery):
    pass
