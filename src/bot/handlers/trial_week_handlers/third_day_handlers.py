from ...init_bot import dp, INIT_DAY_FUNCTIONS
from ...const.msgs import DAY_3_INTRO_MSG, DAY_3_MSG_1, USER_CHARACTERISTIC_1, USER_CHARACTERISTIC_2, DAY_3_MSG_2

import json

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

class FSMStateCharacteristic(StatesGroup):
    state_first_message = State()
    state_second_message = State()


# @dp.message_handler(Text('Начать третий день'))
async def third_day_intro(user_id: str):
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Отправить характеристику')]
    ], resize_keyboard=True)
    user_data = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    user_goal = user_data[user_id]['Цель']
    goal_reason = user_data[user_id]['Зачем цель']
    user_data[user_id]['Был оповещен сегодня'] = 'Да'
    json.dump(user_data, open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'w'), ensure_ascii=False, indent=3)
    await bot.send_message(chat_id=user_id, text=DAY_3_INTRO_MSG, reply_markup=types.ReplyKeyboardRemove())
    await bot.send_message(chat_id=user_id, text=DAY_3_MSG_1.format(user_goal=user_goal, goal_reason=goal_reason), reply_markup=keyboard)


# @dp.message_handler(Text('Отправить характеристику'), state=None)
async def get_user_characteristic_name(message: types.Message):
    await FSMStateCharacteristic.state_first_message.set()
    await message.answer(text=USER_CHARACTERISTIC_1, reply_markup=types.ReplyKeyboardRemove())


# @dp.message_handler(state=FSMStateCharacteristic.state_first_message)
async def get_user_characteristic_value(message: types.Message, state: FSMContext):
    await FSMStateCharacteristic.state_second_message.set()
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Да')],
        [types.KeyboardButton(text='Нет')]
    ], resize_keyboard=True)
    async with state.proxy() as data:
        data['Название характеристики'] = message.text
    await message.answer(text=USER_CHARACTERISTIC_2, reply_markup=keyboard)


# @dp.message_handler(Text(['Да', 'Нет']), state=FSMStateCharacteristic.state_second_message)
async def third_day_last_message(message: types.Message, state: FSMContext):
    user_data = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    user_id = str(message.from_user.id)
    async with state.proxy() as data:
        new_characteristic = {
            'Название характеристики': data['Название характеристики'],
            'Позитивная?': message.text
        }
        user_data[user_id]['Характеристики'].append(new_characteristic)
        user_data[user_id]['Текущий пробный день'] = '4'
        json.dump(user_data, open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'w'), ensure_ascii=False, indent=3)
    await message.answer(text=DAY_3_MSG_2, reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


def register_handlers_third_day(dp: Dispatcher):
    dp.register_message_handler(get_user_characteristic_name, Text('Отправить характеристику'), state=None)
    dp.register_message_handler(get_user_characteristic_value, state=FSMStateCharacteristic.state_first_message)
    dp.register_message_handler(third_day_last_message, Text(['Да', 'Нет']),  state=FSMStateCharacteristic.state_second_message)

INIT_DAY_FUNCTIONS.update({'3': third_day_intro})
