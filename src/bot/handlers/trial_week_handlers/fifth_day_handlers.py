from bot.init_bot import bot, INIT_DAY_FUNCTIONS
from bot.const.msgs import DAY_5_INTRO_MSG, DAY_5_MSG_1, DAY_5_MSG_2, DAY_5_MSG_3, DAY_5_MSG_4
from service.custom_methods import send_message

import json
import os

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

preferences_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../config/user_preferences.json'))


class FSMFiveDay(StatesGroup):
    state_first_message = State()


async def fifth_day_intro(user_id: str):
    await send_message(chat_id=user_id, text=DAY_5_INTRO_MSG, reply_markup=types.ReplyKeyboardRemove())
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Финансовую')],
        [types.KeyboardButton(text='Уверенность')],
        [types.KeyboardButton(text='Здоровье')]
    ], resize_keyboard=True)
    user_data = json.load(open(preferences_path, 'r'))
    main_characteristic = user_data[user_id]['Обращение']
    user_data[user_id]['Был оповещен сегодня'] = 'Да'
    json.dump(user_data, open(preferences_path, 'w'), ensure_ascii=False, indent=3)
    await send_message(chat_id=user_id, text=DAY_5_MSG_1.format(main_characteristic=main_characteristic), reply_markup=keyboard)


async def get_user_sphere(message: types.Message):
    await FSMFiveDay.state_first_message.set()
    await message.answer(text=DAY_5_MSG_2, reply_markup=types.ReplyKeyboardRemove())
    await message.answer(text='(тут запускается алгоритм подбора установок')
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Да')],
        [types.KeyboardButton(text='Нет')]
    ], resize_keyboard=True)
    await message.answer(text=DAY_5_MSG_3, reply_markup=keyboard)


async def get_user_reminder(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Отправить характеристику')],
        [types.KeyboardButton(text='Отправить установку')],
        [types.KeyboardButton(text='Отправить привычку')]
    ], resize_keyboard=True)
    user_data = json.load(open(preferences_path, 'r'))
    user_id = str(message.from_user.id)
    user_data[user_id]['Напоминать об установках'] = message.text
    user_data[user_id]['Текущий пробный день'] = '6'
    json.dump(user_data, open(preferences_path, 'w'), ensure_ascii=False, indent=3)
    await message.answer(text=DAY_5_MSG_4, reply_markup=keyboard)
    await state.finish()


def register_handlers_fifth_day(dp: Dispatcher):
    dp.register_message_handler(get_user_sphere, Text(['Финансовую', 'Уверенность', 'Здоровье']), state=None)
    dp.register_message_handler(get_user_reminder, Text(['Да', 'Нет']), state=FSMFiveDay.state_first_message)


INIT_DAY_FUNCTIONS.update({'5': fifth_day_intro})
