from ...init_bot import dp, INIT_DAY_FUNCTIONS
from ...const.msgs import DAY_5_INTRO_MSG, DAY_5_MSG_1, DAY_5_MSG_2, DAY_5_MSG_3, DAY_5_MSG_4

import json

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

class FSMFiveDay(StatesGroup):
    state_first_message = State()


# @dp.message_handler(Text('Начать пятый день'), state=None)
async def fifth_day_intro(user_id: str):
    await bot.send_message(chat_id=user_id, text=DAY_5_INTRO_MSG, reply_markup=types.ReplyKeyboardRemove())
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Финансовую')],
        [types.KeyboardButton(text='Уверенность')],
        [types.KeyboardButton(text='Здоровье')]
    ], resize_keyboard=True)
    user_data = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    main_characteristic = user_data[user_id]['Обращение']
    user_data[user_id]['Был оповещен сегодня'] = 'Да'
    json.dump(user_data, open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'w'), ensure_ascii=False, indent=3)
    await bot.send_message(chat_id=user_id, text=DAY_5_MSG_1.format(main_characteristic=main_characteristic), reply_markup=keyboard)


# @dp.message_handler(Text(['Финансовую', 'Уверенность', 'Здоровье']), state=None)
async def get_user_sphere(message: types.Message):
    await FSMFiveDay.state_first_message.set()
    await message.answer(text=DAY_5_MSG_2, reply_markup=types.ReplyKeyboardRemove())
    await message.answer(text='(тут запускается алгоритм подбора установок')
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Да')],
        [types.KeyboardButton(text='Нет')]
    ], resize_keyboard=True)
    await message.answer(text=DAY_5_MSG_3, reply_markup=keyboard)


# @dp.message_handler(Text(['Да', 'Нет']), state=FSMFiveDay.state_first_message)
async def get_user_reminder(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Отправить характеристику')],
        [types.KeyboardButton(text='Отправить установку')],
        [types.KeyboardButton(text='Отправить привычку')]
    ], resize_keyboard=True)
    user_data = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    user_id = str(message.from_user.id)
    user_data[user_id]['Напоминать об установках'] = message.text
    user_data[user_id]['Текущий пробный день'] = '6'
    json.dump(user_data, open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'w'), ensure_ascii=False, indent=3)
    await message.answer(text=DAY_5_MSG_4, reply_markup=keyboard)
    await state.finish()


def register_handlers_fifth_day(dp: Dispatcher):
    dp.register_message_handler(get_user_sphere, Text(['Финансовую', 'Уверенность', 'Здоровье']), state=None)
    dp.register_message_handler(get_user_reminder, Text(['Да', 'Нет']), state=FSMFiveDay.state_first_message)

INIT_DAY_FUNCTIONS.update({'5': fifth_day_intro})
