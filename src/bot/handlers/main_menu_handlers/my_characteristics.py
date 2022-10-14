import asyncio
import json
import os

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from ...const.msgs import USER_CHARACTERISTIC_1, USER_CHARACTERISTIC_2
from bot.init_bot import bot

preferences_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../config/user_preferences.json'))

char_number_data = CallbackData('characteristic', 'menu', 'action', 'number')
add_new_char_data = CallbackData('characteristic', 'menu', 'action')

CHARACTERISTIC_INFO_TEMPLATE = '''
Характеристика №{char_number}

<u><b>Название</b></u>
{char_name}

<u><b>Полезная</b></u>
{char_benefit}
'''

CHARACTERISTIC_MSG_TEMPLATE = '''
Список ваших характеристик
'''

EMPTY_CHAR_MSG_TEMPLATE = '''
Вы пока не сохранили ни одной привычки
'''


class FSMStateAddCharacteristic(StatesGroup):
    state_new_char_name = State()
    state_new_char_value = State()


async def show_characteristics_list(message: types.Message):
    user_id = str(message.from_user.id)
    users_data = json.load(open(preferences_path, 'r'))
    user_chars = users_data[user_id]['Характеристики']
    inline_message = types.InlineKeyboardMarkup(row_width=1)
    if user_chars:
        for i, characteristic in enumerate(user_chars):
            char_name = characteristic['Название характеристики']
            inline_message.add(types.InlineKeyboardButton(text=char_name,
                                                          callback_data=char_number_data.new(menu='characteristic',
                                                                                             action='show',
                                                                                             number=i)))
        formatted_msg = CHARACTERISTIC_MSG_TEMPLATE
    else:
        formatted_msg = EMPTY_CHAR_MSG_TEMPLATE
    inline_message.add(types.InlineKeyboardButton(text='Добавить характеристику',
                                                  callback_data=add_new_char_data.new(menu='characteristic', action='add')))
    await message.answer(text=formatted_msg, reply_markup=inline_message, parse_mode='HTML')


async def show_user_characteristic(query: types.CallbackQuery):
    user_id = str(query.from_user.id)
    users_data = json.load(open(preferences_path, 'r'))
    user_chars = users_data[user_id]['Характеристики']
    char_number = int(query.data.split(':')[3])
    char_name = user_chars[char_number]['Название характеристики']
    char_benefit = user_chars[char_number]['Позитивная']
    inline_message = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='Сделать основной', callback_data=char_number_data.new(menu='characteristic',
                                                                                                action='make_main',
                                                                                                number=char_number))],
        [types.InlineKeyboardButton(text='Удалить', callback_data=char_number_data.new(menu='characteristic',
                                                                                       action='remove',
                                                                                       number=char_number))],
        [types.InlineKeyboardButton(text='Назад', callback_data=char_number_data.new(menu='characteristic',
                                                                                     action='back_to_chars',
                                                                                     number=char_number))]
    ])
    formatted_msg = CHARACTERISTIC_INFO_TEMPLATE.format(char_number=char_number, char_name=char_name,
                                                        char_benefit=char_benefit)
    await bot.edit_message_text(text=formatted_msg, chat_id=query.message.chat.id, message_id=query.message.message_id,
                                reply_markup=inline_message, parse_mode='HTML')


async def add_new_user_characteristic_name(query: types.CallbackQuery, state: FSMContext):
    await FSMStateAddCharacteristic.state_new_char_name.set()
    message = await query.message.answer(text=USER_CHARACTERISTIC_1, reply_markup=types.ReplyKeyboardRemove())
    message_id = message.message_id
    async with state.proxy() as data:
        data['inline_msg'] = query.message.message_id
        data['remove_msgs'] = [message_id]


async def add_new_user_characteristic_value(message: types.Message, state: FSMContext):
    await FSMStateAddCharacteristic.state_new_char_value.set()
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Да')],
        [types.KeyboardButton(text='Нет')]
    ], resize_keyboard=True)
    message_from_bot = await message.answer(text=USER_CHARACTERISTIC_2, reply_markup=keyboard)
    message_from_bot_id = message_from_bot.message_id
    async with state.proxy() as data:
        data['char_name'] = message.text
        data['remove_msgs'].append(message_from_bot_id)
        data['remove_msgs'].append(message.message_id)


async def save_new_user_characteristic(message: types.Message, state: FSMContext):
    users_data = json.load(open(preferences_path, 'r'))
    user_id = str(message.from_user.id)
    chat_id = message.chat.id
    async with state.proxy() as data:
        new_char = {
            'Название характеристики': data['char_name'],
            'Позитивная': message.text
        }
        users_data[user_id]['Характеристики'].append(new_char)
    json.dump(users_data, open(preferences_path, 'w'),
              ensure_ascii=False, indent=3)
    user_chars = users_data[user_id]['Характеристики']
    inline_message = types.InlineKeyboardMarkup(row_width=1)
    for i, characteristic in enumerate(user_chars):
        char_name = characteristic['Название характеристики']
        inline_message.add(types.InlineKeyboardButton(text=char_name,
                                                      callback_data=char_number_data.new(menu='characteristic',
                                                                                         action='show',
                                                                                         number=i)))
    inline_message.add(types.InlineKeyboardButton(text='Добавить характеристику',
                                                  callback_data=add_new_char_data.new(menu='characteristic',
                                                                                      action='add')))
    tasks = []
    messages_to_remove = data['remove_msgs'] + [message.message_id]
    for elem in messages_to_remove:
        task = asyncio.create_task(bot.delete_message(chat_id=message.chat.id, message_id=int(elem)))
        tasks.append(task)
    await asyncio.gather(*tasks)
    await bot.edit_message_text(text=CHARACTERISTIC_MSG_TEMPLATE, chat_id=chat_id,
                                message_id=data['inline_msg'], reply_markup=inline_message)
    await state.finish()


async def change_main_charactiristic(query: types.CallbackQuery):
    user_id = str(query.from_user.id)
    users_data = json.load(open(preferences_path, 'r'))
    user_chars = users_data[user_id]['Характеристики']
    new_main_char_num = int(query.data.split(':')[3])
    new_main_char = user_chars[new_main_char_num]['Название характеристики']
    users_data[user_id]['Обращение'] = new_main_char
    json.dump(users_data, open(preferences_path, 'w'),
              ensure_ascii=False, indent=3)
    await query.answer(text=f'Теперь я буду обращаться к вам {new_main_char}', cache_time=10)


async def remove_user_characteristic(query: types.CallbackQuery):
    user_id = str(query.from_user.id)
    char_number = int(query.data.split(':')[3])
    users_data = json.load(open(preferences_path, 'r'))
    users_data[user_id]['Характеристики'].pop(char_number)
    user_chars = users_data[user_id]['Характеристики']
    inline_message = types.InlineKeyboardMarkup(row_width=1)
    if user_chars:
        for i, characteristic in enumerate(user_chars):
            char_name = characteristic['Название характеристики']
            inline_message.add(types.InlineKeyboardButton(text=char_name,
                                                          callback_data=char_number_data.new(menu='characteristic',
                                                                                             action='show',
                                                                                             number=i)))
        formatted_msg = CHARACTERISTIC_MSG_TEMPLATE
    else:
        formatted_msg = EMPTY_CHAR_MSG_TEMPLATE
    inline_message.add(types.InlineKeyboardButton(text='Добавить характеристику',
                                                  callback_data=add_new_char_data.new(menu='characteristic', action='add')))
    json.dump(users_data, open(preferences_path, 'w'),
              indent=3, ensure_ascii=False)
    await bot.edit_message_text(text=formatted_msg, chat_id=query.message.chat.id, message_id=query.message.message_id,
                                reply_markup=inline_message, parse_mode='HTML')


async def back_to_habbits_list(query: types.CallbackQuery):
    user_id = str(query.from_user.id)
    users_data = json.load(open(preferences_path, 'r'))
    user_chars = users_data[user_id]['Характеристики']
    inline_message = types.InlineKeyboardMarkup(row_width=1)
    for i, characteristic in enumerate(user_chars):
        char_name = characteristic['Название характеристики']
        inline_message.add(types.InlineKeyboardButton(text=char_name,
                                                      callback_data=char_number_data.new(menu='characteristic',
                                                                                         action='show',
                                                                                         number=i)))
    inline_message.add(types.InlineKeyboardButton(text='Добавить характеристику',
                                                  callback_data=add_new_char_data.new(menu='characteristic', action='add')))
    formatted_msg = CHARACTERISTIC_MSG_TEMPLATE
    await bot.edit_message_text(text=formatted_msg, chat_id=query.message.chat.id, message_id=query.message.message_id,
                                reply_markup=inline_message, parse_mode='HTML')


def register_my_characteristics_handlers(dp: Dispatcher):
    dp.register_message_handler(show_characteristics_list, Text('Мои характеристики'))
    dp.register_callback_query_handler(show_user_characteristic, char_number_data.filter(menu='characteristic',
                                                                                         action='show'))

    dp.register_callback_query_handler(add_new_user_characteristic_name,
                                       add_new_char_data.filter(menu='characteristic', action='add'), state=None)
    dp.register_message_handler(add_new_user_characteristic_value, state=FSMStateAddCharacteristic.state_new_char_name)
    dp.register_message_handler(save_new_user_characteristic,
                                Text(['Да', 'Нет']), state=FSMStateAddCharacteristic.state_new_char_value)

    dp.register_callback_query_handler(change_main_charactiristic, char_number_data.filter(menu='characteristic',
                                                                                           action='make_main'))
    dp.register_callback_query_handler(remove_user_characteristic, char_number_data.filter(menu='characteristic',
                                                                                           action='remove'))
    dp.register_callback_query_handler(back_to_habbits_list, char_number_data.filter(menu='characteristic',
                                                                                     action='back_to_chars'))
