import asyncio
import json

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# pagination_callback_data = CallbackData('pagination', 'page')
from ...const.msgs import USER_HABBIT_MSG_1, USER_HABBIT_MSG_2, USER_HABBIT_MSG_3
from src.bot.init_bot import bot

habbit_number_data = CallbackData('habbit', 'menu', 'action', 'number')
add_new_habbit_data = CallbackData('habbit', 'menu', 'action') # Нужно ли?

HABBIT_INFO_TEMPLATE = '''
Привычка №{habbit_number}

<u><b>Название</b></u>
{habbit_name}

<u><b>Триггер</b></u>
{habbit_trigger}

<u><b>Приносит пользу</b></u>
{habbit_benefit}
'''

HABBITS_MSG_TEMPLATE = '''
Список ваших привычек
'''

EMPTY_HABBITS_MSG_TEMPLATE = '''
Вы пока не сохранили ни одной привычки
'''


class FSMStateAddHabbit(StatesGroup):
    state_new_habbit_name = State()
    state_new_habbit_trigger = State()
    state_new_habbit_value = State()


class FSMStateRemoveHabbit(StatesGroup):
    state_start_remove = State()


async def show_habbits_list(message: types.Message):
    user_id = str(message.from_user.id)
    users_data = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    user_habbits = users_data[user_id]['Привычки']
    inline_message = types.InlineKeyboardMarkup(row_width=1)
    if user_habbits:
        for i, habbit in enumerate(user_habbits):
            habbit_name = habbit['Название привычки']
            inline_message.add(types.InlineKeyboardButton(text=habbit_name,
                                                          callback_data=habbit_number_data.new(menu='habbit',
                                                                                               action='show',
                                                                                               number=i)))
        formatted_msg = HABBITS_MSG_TEMPLATE
    else:
        formatted_msg = EMPTY_HABBITS_MSG_TEMPLATE
    inline_message.add(types.InlineKeyboardButton(text='Добавить привычку',
                                                  callback_data=add_new_habbit_data.new(menu='habbit', action='add')))
    await message.answer(text=formatted_msg, reply_markup=inline_message, parse_mode='HTML')


async def show_user_habbit(query: types.CallbackQuery):
    user_id = str(query.from_user.id)
    users_data = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    user_habbits = users_data[user_id]['Привычки']
    habbit_number = int(query.data.split(':')[3])
    habbit_name = user_habbits[habbit_number]['Название привычки']
    habbit_trigger = user_habbits[habbit_number]['Триггер']
    habbit_benefit = user_habbits[habbit_number]['Полезна?']
    inline_message = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='Удалить', callback_data=habbit_number_data.new(menu='habbit',
                                                                                         action='remove',
                                                                                         number=habbit_number))],
        [types.InlineKeyboardButton(text='Назад', callback_data=habbit_number_data.new(menu='habbit',
                                                                                       action='back_to_habbits',
                                                                                       number=habbit_number))]
    ])
    formatted_msg = HABBIT_INFO_TEMPLATE.format(habbit_number=habbit_number, habbit_name=habbit_name,
                                                habbit_trigger=habbit_trigger, habbit_benefit=habbit_benefit)
    await bot.edit_message_text(text=formatted_msg, chat_id=query.message.chat.id,
                                message_id=query.message.message_id, reply_markup=inline_message, parse_mode='HTML')


async def add_new_user_habbit_name(query: types.CallbackQuery, state: FSMContext):
    await FSMStateAddHabbit.state_new_habbit_name.set()
    message = await bot.send_message(chat_id=query.message.chat.id, text=USER_HABBIT_MSG_1)
    message_id = message.message_id
    async with state.proxy() as data:
        data['inline_msg'] = query.message.message_id
        data['remove_msgs'] = [message_id]


async def add_new_user_habbit_trigger(message: types.Message, state: FSMContext):
    await FSMStateAddHabbit.state_new_habbit_trigger.set()
    message_from_bot = await message.answer(text=USER_HABBIT_MSG_2)
    message_from_bot_id = message_from_bot.message_id
    async with state.proxy() as data:
        data['remove_msgs'].append(message_from_bot_id)
        data['remove_msgs'].append(message.message_id)
        data['Название привычки'] = message.text


async def add_new_user_habbit_value(message: types.Message, state: FSMContext):
    await FSMStateAddHabbit.state_new_habbit_value.set()
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Да')],
        [types.KeyboardButton(text='Нет')]
    ], resize_keyboard=True)
    message_from_bot = await message.answer(text=USER_HABBIT_MSG_3, reply_markup=keyboard)
    message_from_bot_id = message_from_bot.message_id
    async with state.proxy() as data:
        data['remove_msgs'].append(message_from_bot_id)
        data['remove_msgs'].append(message.message_id)
        data['Триггер привычки'] = message.text


async def save_new_user_habbit(message: types.Message, state=FSMContext):
    users_data = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    user_id = str(message.from_user.id)
    chat_id = message.chat.id
    async with state.proxy() as data:
        new_habit = {
            'Название привычки': data['Название привычки'],
            'Триггер': data['Триггер привычки'],
            'Полезна?': message.text
        }
        users_data[user_id]['Привычки'].append(new_habit)
        json.dump(users_data, open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'w'),
                  ensure_ascii=False, indent=3)
    user_habbits = users_data[user_id]['Привычки']
    inline_message = types.InlineKeyboardMarkup(row_width=1)
    for i, habbit in enumerate(user_habbits):
        habbit_name = habbit['Название привычки']
        inline_message.add(types.InlineKeyboardButton(text=habbit_name,
                                                      callback_data=habbit_number_data.new(menu='habbit',
                                                                                           action='show',
                                                                                           number=i)))
    inline_message.add(types.InlineKeyboardButton(text='Добавить привычку',
                                                  callback_data=add_new_habbit_data.new(menu='habbit',
                                                                                        action='add')))
    tasks = []
    messages_to_remove = data['remove_msgs'] + [message.message_id]
    for elem in messages_to_remove:
        task = asyncio.create_task(bot.delete_message(chat_id=message.chat.id, message_id=int(elem)))
        tasks.append(task)
    await asyncio.gather(*tasks)
    await bot.edit_message_text(text=HABBITS_MSG_TEMPLATE, chat_id=chat_id,
                                message_id=data['inline_msg'], reply_markup=inline_message)
    await state.finish()


async def remove_user_habbit(query: types.CallbackQuery):
    user_id = str(query.from_user.id)
    habbit_number = int(query.data.split(':')[3])
    users_data = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    users_data[user_id]['Привычки'].pop(habbit_number)
    user_habbits = users_data[user_id]['Привычки']
    inline_message = types.InlineKeyboardMarkup(row_width=1)
    if user_habbits:
        for i, habbit in enumerate(user_habbits):
            habbit_name = habbit['Название привычки']
            inline_message.add(types.InlineKeyboardButton(text=habbit_name,
                                                          callback_data=habbit_number_data.new(menu='habbit',
                                                                                               action='show',
                                                                                               number=i)))
        formatted_msg = HABBITS_MSG_TEMPLATE
    else:
        formatted_msg = EMPTY_HABBITS_MSG_TEMPLATE
    inline_message.add(types.InlineKeyboardButton(text='Добавить привычку',
                                                  callback_data=add_new_habbit_data.new(menu='habbit', action='add')))
    json.dump(users_data, open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'w'),
              indent=3, ensure_ascii=False)
    await bot.edit_message_text(text=formatted_msg, chat_id=query.message.chat.id, message_id=query.message.message_id,
                                reply_markup=inline_message, parse_mode='HTML')


async def back_to_habbits_list(query: types.CallbackQuery):
    user_id = str(query.from_user.id)
    users_data = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    user_habbits = users_data[user_id]['Привычки']
    inline_message = types.InlineKeyboardMarkup(row_width=1)
    for i, habbit in enumerate(user_habbits):
        habbit_name = habbit['Название привычки']
        inline_message.add(types.InlineKeyboardButton(text=habbit_name,
                                                      callback_data=habbit_number_data.new(menu='habbit',
                                                                                           action='show',
                                                                                           number=i)))
    inline_message.add(types.InlineKeyboardButton(text='Добавить привычку',
                                                  callback_data=add_new_habbit_data.new(menu='habbit', action='add')))
    formatted_msg = HABBITS_MSG_TEMPLATE
    await bot.edit_message_text(text=formatted_msg, chat_id=query.message.chat.id, message_id=query.message.message_id,
                                reply_markup=inline_message, parse_mode='HTML')


def register_my_habbits_handlers(dp: Dispatcher):
    dp.register_message_handler(show_habbits_list, Text('Мои привычки'))
    dp.register_callback_query_handler(show_user_habbit, habbit_number_data.filter(menu='habbit', action='show'))

    dp.register_callback_query_handler(add_new_user_habbit_name,
                                       add_new_habbit_data.filter(menu='habbit', action='add'), state=None)
    dp.register_message_handler(add_new_user_habbit_trigger, state=FSMStateAddHabbit.state_new_habbit_name)
    dp.register_message_handler(add_new_user_habbit_value, state=FSMStateAddHabbit.state_new_habbit_trigger)
    dp.register_message_handler(save_new_user_habbit, Text(['Да', 'Нет']),
                                state=FSMStateAddHabbit.state_new_habbit_value)

    dp.register_callback_query_handler(remove_user_habbit, habbit_number_data.filter(menu='habbit', action='remove'))
    dp.register_callback_query_handler(back_to_habbits_list,
                                       habbit_number_data.filter(menu='habbit', action='back_to_habbits'))
