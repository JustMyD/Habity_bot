from ...init_bot import dp, INIT_DAY_FUNCTIONS
from ...const.msgs import DAY_2_INTRO_MSG, DAY_2_MSG_1, USER_ATTITUDE_MSG_1, USER_ATTITUDE_MSG_2, DAY_2_MSG_2

import json

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

class FSMStateAttitude(StatesGroup):
    state_first_message = State()
    state_second_message = State()


# @dp.message_handler(Text('Начать второй день'))
async def second_day_intro(user_id: str):
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Отправить установку')]
    ], resize_keyboard=True)
    user_data = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    user_data[user_id]['Был оповещен сегодня'] = 'Да'
    json.dump(user_data, open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'w'), ensure_ascii=False, indent=3)
    await bot.send_message(chat_id=user_id, text=DAY_2_INTRO_MSG, reply_markup=types.ReplyKeyboardRemove())
    await bot.send_message(chat_id=user_id, text=DAY_2_MSG_1, reply_markup=keyboard)


# @dp.message_handler(Text('Отправить установку'), state=None)
async def get_user_attitude_name(message: types.Message):
    await FSMStateAttitude.state_first_message.set()
    await message.answer(text=USER_ATTITUDE_MSG_1, reply_markup=types.ReplyKeyboardRemove())


# @dp.message_handler(state=FSMStateAttitude.state_first_message)
async def get_user_attitude_value(message: types.Message, state: FSMContext):
    await FSMStateAttitude.state_second_message.set()
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Да')],
        [types.KeyboardButton(text='Нет')]
    ], resize_keyboard=True)
    async with state.proxy() as data:
        data['Название установки'] = message.text
    await message.answer(text=USER_ATTITUDE_MSG_2, reply_markup=keyboard)


# @dp.message_handler(Text(['Да', 'Нет']), state=FSMStateAttitude.state_second_message)
async def second_day_last_message(message: types.Message, state: FSMContext):
    user_data = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    user_id = str(message.from_user.id)
    async with state.proxy() as data:
        new_attitude = {
            'Название установки': data['Название установки'],
            'Полезна?': message.text
        }
        user_data[user_id]['Установки'].append(new_attitude)
        user_data[user_id]['Текущий пробный день'] = '3'
        json.dump(user_data, open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'w'), ensure_ascii=False, indent=3)
    await message.answer(text=DAY_2_MSG_2, reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


def register_handlers_second_day(dp: Dispatcher):
    dp.register_message_handler(get_user_attitude_name, Text('Отправить установку'), state=None)
    dp.register_message_handler(get_user_attitude_value, state=FSMStateAttitude.state_first_message)
    dp.register_message_handler(second_day_last_message, Text(['Да', 'Нет']),  state=FSMStateAttitude.state_second_message)

INIT_DAY_FUNCTIONS.update({'2': second_day_intro})
