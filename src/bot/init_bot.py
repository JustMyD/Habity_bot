"""
Пока все колбэки здесь в одной куче, нужно раскидать TrialDays функции по отдельным скриптам, в init скрипте
остаются основные колбэки
"""
from .const.msgs import MAIN_MENU_MSG

import json
import os

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from dotenv import load_dotenv

load_dotenv()
INIT_DAY_FUNCTIONS = {}

bot = Bot(token=os.getenv('API_TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

preferences_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../config/user_preferences.json'))


@dp.message_handler(commands='menu')
async def show_main_menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Моя цель')],
        [types.KeyboardButton(text='Мои привычки')],
        [types.KeyboardButton(text='Мои характеристики')],
        [types.KeyboardButton(text='Мои установки')],
        [types.KeyboardButton(text='Настройки')]
    ])
    user_data = json.load(open(preferences_path, 'r'))
    main_characteristic = user_data[str(message.from_user.id)]['Обращение']
    main_characteristic = main_characteristic if main_characteristic else 'Друг'
    await message.answer(text=MAIN_MENU_MSG.format(characteristic=main_characteristic), reply_markup=keyboard)
