import asyncio
import json
import os

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# pagination_callback_data = CallbackData('pagination', 'page')
from bot.const.msgs import USER_HABIT_MSG_1, USER_HABIT_MSG_2, USER_HABIT_MSG_3
from bot.init_bot import bot

preferences_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../config/user_preferences.json'))

habit_number_data = CallbackData('habit', 'menu', 'action', 'number')
add_new_habit_data = CallbackData('habit', 'menu', 'action')  # Нужно ли?

HABIT_INFO_TEMPLATE = '''
Привычка №{habit_number}

<u><b>Название</b></u>
{habit_name}

<u><b>Триггер</b></u>
{habit_trigger}

<u><b>Приносит пользу</b></u>
{habit_benefit}
'''

HABITS_MSG_TEMPLATE = '''
Список ваших привычек
'''

EMPTY_HABITS_MSG_TEMPLATE = '''
Вы пока не сохранили ни одной привычки
'''


class FSMStateAddHabbit(StatesGroup):
    state_new_habit_name = State()
    state_new_habit_trigger = State()
    state_new_habit_value = State()


class FSMStateRemoveHabbit(StatesGroup):
    state_start_remove = State()


async def show_habits_list(message: types.Message):
    user_id = str(message.from_user.id)
    users_data = json.load(open(preferences_path, 'r'))
    user_habits = users_data[user_id]['Привычки']
    inline_message = types.InlineKeyboardMarkup(row_width=1)
    if user_habits:
        for i, habit in enumerate(user_habits):
            habit_name = habit['Название привычки']
            inline_message.add(types.InlineKeyboardButton(text=habit_name,
                                                          callback_data=habit_number_data.new(menu='habit',
                                                                                              action='show',
                                                                                              number=i)))
        formatted_msg = HABITS_MSG_TEMPLATE
    else:
        formatted_msg = EMPTY_HABITS_MSG_TEMPLATE
    inline_message.add(types.InlineKeyboardButton(text='Добавить привычку',
                                                  callback_data=add_new_habit_data.new(menu='habit', action='add')))
    await message.answer(text=formatted_msg, reply_markup=inline_message, parse_mode='HTML')


async def show_user_habit(query: types.CallbackQuery):
    user_id = str(query.from_user.id)
    users_data = json.load(open(preferences_path, 'r'))
    user_habits = users_data[user_id]['Привычки']
    habit_number = int(query.data.split(':')[3])
    habit_name = user_habits[habit_number]['Название привычки']
    habit_trigger = user_habits[habit_number]['Триггер']
    habit_benefit = user_habits[habit_number]['Полезна?']
    inline_message = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='Удалить', callback_data=habit_number_data.new(menu='habit',
                                                                                        action='remove',
                                                                                        number=habit_number))],
        [types.InlineKeyboardButton(text='Назад', callback_data=habit_number_data.new(menu='habit',
                                                                                      action='back_to_habits',
                                                                                      number=habit_number))]
    ])
    formatted_msg = HABIT_INFO_TEMPLATE.format(habit_number=habit_number, habit_name=habit_name,
                                               habit_trigger=habit_trigger, habit_benefit=habit_benefit)
    await bot.edit_message_text(text=formatted_msg, chat_id=query.message.chat.id,
                                message_id=query.message.message_id, reply_markup=inline_message, parse_mode='HTML')


async def add_new_user_habit_name(query: types.CallbackQuery, state: FSMContext):
    await FSMStateAddHabbit.state_new_habit_name.set()
    message = await bot.send_message(chat_id=query.message.chat.id, text=USER_HABIT_MSG_1)
    message_id = message.message_id
    async with state.proxy() as data:
        data['inline_msg'] = query.message.message_id
        data['remove_msgs'] = [message_id]


async def add_new_user_habit_trigger(message: types.Message, state: FSMContext):
    await FSMStateAddHabbit.state_new_habit_trigger.set()
    message_from_bot = await message.answer(text=USER_HABIT_MSG_2)
    message_from_bot_id = message_from_bot.message_id
    async with state.proxy() as data:
        data['remove_msgs'].append(message_from_bot_id)
        data['remove_msgs'].append(message.message_id)
        data['Название привычки'] = message.text


async def add_new_user_habit_value(message: types.Message, state: FSMContext):
    await FSMStateAddHabbit.state_new_habit_value.set()
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Да')],
        [types.KeyboardButton(text='Нет')]
    ], resize_keyboard=True)
    message_from_bot = await message.answer(text=USER_HABIT_MSG_3, reply_markup=keyboard)
    message_from_bot_id = message_from_bot.message_id
    async with state.proxy() as data:
        data['remove_msgs'].append(message_from_bot_id)
        data['remove_msgs'].append(message.message_id)
        data['Триггер привычки'] = message.text


async def save_new_user_habit(message: types.Message, state=FSMContext):
    users_data = json.load(open(preferences_path, 'r'))
    user_id = str(message.from_user.id)
    chat_id = message.chat.id
    async with state.proxy() as data:
        new_habit = {
            'Название привычки': data['Название привычки'],
            'Триггер': data['Триггер привычки'],
            'Полезна?': message.text
        }
        users_data[user_id]['Привычки'].append(new_habit)
        json.dump(users_data, open(preferences_path, 'w'),
                  ensure_ascii=False, indent=3)
    user_habits = users_data[user_id]['Привычки']
    inline_message = types.InlineKeyboardMarkup(row_width=1)
    for i, habit in enumerate(user_habits):
        habit_name = habit['Название привычки']
        inline_message.add(types.InlineKeyboardButton(text=habit_name,
                                                      callback_data=habit_number_data.new(menu='habit',
                                                                                          action='show',
                                                                                          number=i)))
    inline_message.add(types.InlineKeyboardButton(text='Добавить привычку',
                                                  callback_data=add_new_habit_data.new(menu='habit',
                                                                                       action='add')))
    tasks = []
    messages_to_remove = data['remove_msgs'] + [message.message_id]
    for elem in messages_to_remove:
        task = asyncio.create_task(bot.delete_message(chat_id=message.chat.id, message_id=int(elem)))
        tasks.append(task)
    await asyncio.gather(*tasks)
    await bot.edit_message_text(text=HABITS_MSG_TEMPLATE, chat_id=chat_id,
                                message_id=data['inline_msg'], reply_markup=inline_message)
    await state.finish()


async def remove_user_habit(query: types.CallbackQuery):
    user_id = str(query.from_user.id)
    habit_number = int(query.data.split(':')[3])
    users_data = json.load(open(preferences_path, 'r'))
    users_data[user_id]['Привычки'].pop(habit_number)
    user_habits = users_data[user_id]['Привычки']
    inline_message = types.InlineKeyboardMarkup(row_width=1)
    if user_habits:
        for i, habit in enumerate(user_habits):
            habit_name = habit['Название привычки']
            inline_message.add(types.InlineKeyboardButton(text=habit_name,
                                                          callback_data=habit_number_data.new(menu='habit',
                                                                                              action='show',
                                                                                              number=i)))
        formatted_msg = HABITS_MSG_TEMPLATE
    else:
        formatted_msg = EMPTY_HABITS_MSG_TEMPLATE
    inline_message.add(types.InlineKeyboardButton(text='Добавить привычку',
                                                  callback_data=add_new_habit_data.new(menu='habit', action='add')))
    json.dump(users_data, open(preferences_path, 'w'),
              indent=3, ensure_ascii=False)
    await bot.edit_message_text(text=formatted_msg, chat_id=query.message.chat.id, message_id=query.message.message_id,
                                reply_markup=inline_message, parse_mode='HTML')


async def back_to_habits_list(query: types.CallbackQuery):
    user_id = str(query.from_user.id)
    users_data = json.load(open(preferences_path, 'r'))
    user_habits = users_data[user_id]['Привычки']
    inline_message = types.InlineKeyboardMarkup(row_width=1)
    for i, habit in enumerate(user_habits):
        habit_name = habit['Название привычки']
        inline_message.add(types.InlineKeyboardButton(text=habit_name,
                                                      callback_data=habit_number_data.new(menu='habit',
                                                                                          action='show',
                                                                                          number=i)))
    inline_message.add(types.InlineKeyboardButton(text='Добавить привычку',
                                                  callback_data=add_new_habit_data.new(menu='habit', action='add')))
    formatted_msg = HABITS_MSG_TEMPLATE
    await bot.edit_message_text(text=formatted_msg, chat_id=query.message.chat.id, message_id=query.message.message_id,
                                reply_markup=inline_message, parse_mode='HTML')


def register_my_habits_handlers(dp: Dispatcher):
    dp.register_message_handler(show_habits_list, Text('Мои привычки'))
    dp.register_callback_query_handler(show_user_habit, habit_number_data.filter(menu='habit', action='show'))

    dp.register_callback_query_handler(add_new_user_habit_name,
                                       add_new_habit_data.filter(menu='habit', action='add'), state=None)
    dp.register_message_handler(add_new_user_habit_trigger, state=FSMStateAddHabbit.state_new_habit_name)
    dp.register_message_handler(add_new_user_habit_value, state=FSMStateAddHabbit.state_new_habit_trigger)
    dp.register_message_handler(save_new_user_habit, Text(['Да', 'Нет']),
                                state=FSMStateAddHabbit.state_new_habit_value)

    dp.register_callback_query_handler(remove_user_habit, habit_number_data.filter(menu='habit', action='remove'))
    dp.register_callback_query_handler(back_to_habits_list,
                                       habit_number_data.filter(menu='habit', action='back_to_habits'))
