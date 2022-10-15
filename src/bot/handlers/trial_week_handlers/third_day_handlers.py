from bot.init_bot import bot, INIT_DAY_FUNCTIONS
from bot.const.msgs import DAY_3_INTRO_MSG, DAY_3_MSG_1, USER_CHARACTERISTIC_1, USER_CHARACTERISTIC_2, DAY_3_MSG_2
from service.custom_methods import send_message

import json
import os

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

preferences_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../config/user_preferences.json'))


class FSMStateCharacteristic(StatesGroup):
    state_first_message = State()
    state_second_message = State()


async def third_day_intro(user_id: str):
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Отправить характеристику')]
    ], resize_keyboard=True)
    user_data = json.load(open(preferences_path, 'r'))
    user_goal = user_data[user_id]['Цель']
    goal_reason = user_data[user_id]['Зачем цель']
    user_data[user_id]['Был оповещен сегодня'] = 'Да'
    json.dump(user_data, open(preferences_path, 'w'), ensure_ascii=False, indent=3)
    await send_message(chat_id=user_id, text=DAY_3_INTRO_MSG, reply_markup=types.ReplyKeyboardRemove())
    await send_message(chat_id=user_id, text=DAY_3_MSG_1.format(user_goal=user_goal, goal_reason=goal_reason), reply_markup=keyboard)


async def get_user_characteristic_name(message: types.Message):
    await FSMStateCharacteristic.state_first_message.set()
    await message.answer(text=USER_CHARACTERISTIC_1, reply_markup=types.ReplyKeyboardRemove())


async def get_user_characteristic_value(message: types.Message, state: FSMContext):
    await FSMStateCharacteristic.state_second_message.set()
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Да')],
        [types.KeyboardButton(text='Нет')]
    ], resize_keyboard=True)
    async with state.proxy() as data:
        data['Название характеристики'] = message.text
    await message.answer(text=USER_CHARACTERISTIC_2, reply_markup=keyboard)


async def third_day_last_message(message: types.Message, state: FSMContext):
    user_data = json.load(open(preferences_path, 'r'))
    user_id = str(message.from_user.id)
    async with state.proxy() as data:
        new_characteristic = {
            'Название характеристики': data['Название характеристики'],
            'Позитивная?': message.text
        }
        user_data[user_id]['Характеристики'].append(new_characteristic)
        user_data[user_id]['Текущий пробный день'] = '4'
        json.dump(user_data, open(preferences_path, 'w'), ensure_ascii=False, indent=3)
    await message.answer(text=DAY_3_MSG_2, reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


def register_handlers_third_day(dp: Dispatcher):
    dp.register_message_handler(get_user_characteristic_name, Text('Отправить характеристику'), state=None)
    dp.register_message_handler(get_user_characteristic_value, state=FSMStateCharacteristic.state_first_message)
    dp.register_message_handler(third_day_last_message, Text(['Да', 'Нет']),  state=FSMStateCharacteristic.state_second_message)


INIT_DAY_FUNCTIONS.update({'3': third_day_intro})
