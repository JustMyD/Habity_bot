from bot.init_bot import bot, INIT_DAY_FUNCTIONS
from bot.const.msgs import DAY_4_INTRO_MSG, DAY_4_MSG_1, DAY_4_MSG_2, DAY_4_MSG_3, DAY_4_MSG_4, DAY_4_MSG_5
from service.custom_methods import send_message

import json
import time
import os

from aiogram import Dispatcher, types
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

preferences_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../config/user_preferences.json'))

characteristic_callback_data = CallbackData('characteristic', 'name', 'action')


class FSMFourthDay(StatesGroup):
    state_first_message = State()


async def fourth_day_intro(user_id: str):
    await send_message(chat_id=user_id, text=DAY_4_INTRO_MSG, reply_markup=types.ReplyKeyboardRemove())
    await send_message(chat_id=user_id, text=DAY_4_MSG_1)
    inline_message = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='Мистер', callback_data=characteristic_callback_data.new('Мистер', 'choose'))],
        [types.InlineKeyboardButton(text='Молодой человек',
                                    callback_data=characteristic_callback_data.new('Молодой человек', 'choose'))],
        [types.InlineKeyboardButton(text='Мисс', callback_data=characteristic_callback_data.new('Мисс', 'choose'))],
        [types.InlineKeyboardButton(text='Леди', callback_data=characteristic_callback_data.new('Леди', 'choose'))],
        [types.InlineKeyboardButton(text='Миссис', callback_data=characteristic_callback_data.new('Миссис', 'choose'))],
        [types.InlineKeyboardButton(text='Мадам', callback_data=characteristic_callback_data.new('Мадам', 'choose'))]
    ], row_width=1)
    user_data = json.load(open(preferences_path, 'r'))
    user_data[user_id]['Был оповещен сегодня'] = 'Да'
    json.dump(user_data, open(preferences_path, 'w'),
              ensure_ascii=False, indent=3)
    await send_message(chat_id=user_id, text=DAY_4_MSG_2, reply_markup=inline_message)


async def get_new_user_characteristic(query: types.CallbackQuery):
    await FSMFourthDay.state_first_message.set()
    user_data = json.load(open(preferences_path, 'r'))
    user_id = str(query.from_user.id)
    chat_id = str(query.message.chat.id)
    main_characteristic = query.data.split(':')[1]
    user_data[user_id]['Обращение'] = main_characteristic
    user_data[user_id]['Текущий пробный день'] = '5'
    json.dump(user_data, open(preferences_path, 'w'),
              ensure_ascii=False, indent=3)
    await query.answer(text=DAY_4_MSG_3.format(main_characteristic=main_characteristic), show_alert=True)
    await bot.send_message(chat_id=chat_id, text='(тут запускается алгоритм подбора характеристик')
    time.sleep(1)
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Да')]
    ], resize_keyboard=True)
    await bot.send_message(chat_id=chat_id, text=DAY_4_MSG_4, reply_markup=keyboard)


async def get_user_characteristic_confirm(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Отправить характеристику')],
        [types.KeyboardButton(text='Отправить установку')],
        [types.KeyboardButton(text='Отправить привычку')]
    ], resize_keyboard=True)
    await message.answer(text=DAY_4_MSG_5, reply_markup=keyboard)
    await state.finish()


def register_handlers_fourth_day(dp: Dispatcher):
    dp.register_callback_query_handler(get_new_user_characteristic,
                                       characteristic_callback_data.filter(action='choose'),
                                       state=None)
    dp.register_message_handler(get_user_characteristic_confirm, Text('Да'), state=FSMFourthDay.state_first_message)


INIT_DAY_FUNCTIONS.update({'4': fourth_day_intro})
