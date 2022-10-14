import asyncio
import json
import os

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot.init_bot import bot

preferences_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../config/user_preferences.json'))

arrow_callback_data = CallbackData('arrow', 'type', 'direction', 'next')
control_callback_data = CallbackData('control', 'type', 'action', 'btn_num')

ATTITUDE_INFO_TEMPLATE = '''
<u><b>Установка</b></u>
{attitude_name}

<u><b>Сфера</b></u>
{attitude_sphere}

<u><b>Напоминать</b></u>
{attitude_reminder}
'''

EMPTY_ATTITUDES_MSG_TEMPLATE = '''
Вы пока не сохранили ни одной привычки
'''

ADD_ATTITUDE_MSG_1 = '''
Введите установку, например:
Я люблю подтягиваться, с каждым повтором мое тело становиться рельефнее и я чувствую себя лучше 
'''

ADD_ATTITUDE_MSG_2 = '''
Выберите сферу, на улучшение которой направлена установка
'''

ADD_ATTITUDE_MSG_3 = '''
Во сколько ты хочешь чтобы я напоминал тебе об установке
'''


class FSMStateAddAttitude(StatesGroup):
    state_new_attitude_name = State()
    state_new_attitude_sphere = State()
    state_new_attitude_reminder = State()


async def show_user_attitude(message: types.Message):
    user_id = str(message.from_user.id)
    users_data = json.load(open(preferences_path, 'r'))
    user_attitudes = users_data[user_id]['Установки']
    current_attitude = 0
    inline_message = types.InlineKeyboardMarkup(row_width=1)
    if user_attitudes:
        last_attitude = len(user_attitudes) - 1
        left_arrow_data = arrow_callback_data.new(type='arrow', direction='left', next=str(last_attitude))
        right_arrow_data = arrow_callback_data.new(type='arrow', direction='right', next='1')
        remove_data = control_callback_data.new(type='control', action='remove', btn_num=current_attitude)

        inline_message.row(types.InlineKeyboardButton(text='<', callback_data=left_arrow_data),
                           types.InlineKeyboardButton(text='>', callback_data=right_arrow_data))
        inline_message.add(types.InlineKeyboardButton(text='Удалить', callback_data=remove_data))

        attitude_name = user_attitudes[current_attitude]['Название установки']
        attitude_sphere = user_attitudes[current_attitude]['Сфера']
        attitude_reminder = user_attitudes[current_attitude]['Напоминать']
        formatted_msg = ATTITUDE_INFO_TEMPLATE.format(attitude_name=attitude_name, attitude_sphere=attitude_sphere, attitude_reminder=attitude_reminder)
    else:
        formatted_msg = EMPTY_ATTITUDES_MSG_TEMPLATE
    append_data = control_callback_data.new(type='control', action='append', btn_num=current_attitude)
    inline_message.add(types.InlineKeyboardButton(text='Добавить новую', callback_data=append_data))
    await message.answer(text=formatted_msg, parse_mode='HTML', reply_markup=inline_message)


async def show_previous_user_attitude(query: types.CallbackQuery):
    user_id = str(query.from_user.id)
    users_data = json.load(open(preferences_path, 'r'))
    user_attitudes = users_data[user_id]['Установки']
    current_attitude = int(query.data.split(':')[3])
    inline_message = types.InlineKeyboardMarkup(row_width=1)
    if len(user_attitudes) == 0:
        left_arrow_next = 'null'
        right_arrow_next = 'null'
    elif current_attitude > 0:
        left_arrow_next = current_attitude - 1
        right_arrow_next = current_attitude
    elif current_attitude == 0:
        left_arrow_next = len(user_attitudes) - 1
        right_arrow_next = 1
    left_arrow_data = arrow_callback_data.new(type='arrow', direction='left', next=str(left_arrow_next))
    right_arrow_data = arrow_callback_data.new(type='arrow', direction='right', next=str(right_arrow_next))
    append_data = control_callback_data.new(type='control', action='append', btn_num=current_attitude)
    remove_data = control_callback_data.new(type='control', action='remove', btn_num=current_attitude)

    inline_message.row(types.InlineKeyboardButton(text='<', callback_data=left_arrow_data),
                       types.InlineKeyboardButton(text='>', callback_data=right_arrow_data))
    inline_message.add(types.InlineKeyboardButton(text='Удалить', callback_data=remove_data))
    inline_message.add(types.InlineKeyboardButton(text='Добавить новую', callback_data=append_data))

    attitude_name = user_attitudes[current_attitude]['Название установки']
    attitude_sphere = user_attitudes[current_attitude]['Сфера']
    attitude_reminder = user_attitudes[current_attitude]['Напоминать']
    formatted_msg = ATTITUDE_INFO_TEMPLATE.format(attitude_name=attitude_name, attitude_sphere=attitude_sphere, attitude_reminder=attitude_reminder)
    await bot.edit_message_text(text=formatted_msg, chat_id=query.message.chat.id,
                                message_id=query.message.message_id, parse_mode='HTML', reply_markup=inline_message)


async def show_next_user_attitude(query: types.CallbackQuery):
    user_id = str(query.from_user.id)
    users_data = json.load(open(preferences_path, 'r'))
    user_attitudes = users_data[user_id]['Установки']
    current_attitude = int(query.data.split(':')[3])
    last_attitude = len(user_attitudes) - 1
    inline_message = types.InlineKeyboardMarkup(row_width=1)
    if len(user_attitudes) == 0:
        left_arrow_next = 'null'
        right_arrow_next = 'null'
    elif current_attitude < last_attitude:
        left_arrow_next = current_attitude
        right_arrow_next = current_attitude + 1
    elif current_attitude == last_attitude:
        left_arrow_next = current_attitude
        right_arrow_next = 0
    left_arrow_data = arrow_callback_data.new(type='arrow', direction='left', next=str(left_arrow_next))
    right_arrow_data = arrow_callback_data.new(type='arrow', direction='right', next=str(right_arrow_next))
    append_data = control_callback_data.new(type='control', action='append', btn_num=current_attitude)
    remove_data = control_callback_data.new(type='control', action='remove', btn_num=current_attitude)

    inline_message.row(types.InlineKeyboardButton(text='<', callback_data=left_arrow_data),
                       types.InlineKeyboardButton(text='>', callback_data=right_arrow_data))
    inline_message.add(types.InlineKeyboardButton(text='Удалить', callback_data=remove_data))
    inline_message.add(types.InlineKeyboardButton(text='Добавить новую', callback_data=append_data))

    attitude_name = user_attitudes[current_attitude]['Название установки']
    attitude_sphere = user_attitudes[current_attitude]['Сфера']
    attitude_reminder = user_attitudes[current_attitude]['Напоминать']
    formatted_msg = ATTITUDE_INFO_TEMPLATE.format(attitude_name=attitude_name, attitude_sphere=attitude_sphere, attitude_reminder=attitude_reminder)
    await bot.edit_message_text(text=formatted_msg, chat_id=query.message.chat.id,
                                message_id=query.message.message_id, parse_mode='HTML', reply_markup=inline_message)


async def show_empty_user_attitudes(query: types.CallbackQuery):
    inline_message = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='Добавить установку', callback_data='test:1')]
    ])
    formatted_msg = EMPTY_ATTITUDES_MSG_TEMPLATE
    await bot.edit_message_text(text=formatted_msg, chat_id=query.message.chat.id,
                                message_id=query.message.message_id, parse_mode='HTML', reply_markup=inline_message)


async def remove_user_attitude(query: types.CallbackQuery):
    user_id = str(query.from_user.id)
    users_data = json.load(open(preferences_path, 'r'))
    user_attitudes = users_data[user_id]['Установки']
    current_attitude = int(query.data.split(':')[3])
    user_attitudes.pop(current_attitude)
    json.dump(users_data, open(preferences_path, 'w'),
              ensure_ascii=False, indent=3)
    current_attitude = 0
    inline_message = types.InlineKeyboardMarkup()
    if user_attitudes:
        last_attitude = len(user_attitudes) - 1
        left_arrow_data = arrow_callback_data.new(type='arrow', direction='left', next=str(last_attitude))
        right_arrow_data = arrow_callback_data.new(type='arrow', direction='right', next='1')
        remove_data = control_callback_data.new(type='control', action='remove', btn_num=current_attitude)

        inline_message.row(types.InlineKeyboardButton(text='<', callback_data=left_arrow_data),
                           types.InlineKeyboardButton(text='>', callback_data=right_arrow_data))
        inline_message.add(types.InlineKeyboardButton(text='Удалить', callback_data=remove_data))

        attitude_name = user_attitudes[current_attitude]['Название установки']
        attitude_sphere = user_attitudes[current_attitude]['Сфера']
        formatted_msg = ATTITUDE_INFO_TEMPLATE.format(attitude_name=attitude_name, attitude_sphere=attitude_sphere)
    else:
        formatted_msg = EMPTY_ATTITUDES_MSG_TEMPLATE
    append_data = control_callback_data.new(type='control', action='append', btn_num=current_attitude)
    inline_message.add(types.InlineKeyboardButton(text='Добавить новую', callback_data=append_data))
    await bot.edit_message_text(text=formatted_msg, chat_id=query.message.chat.id,
                                message_id=query.message.message_id, parse_mode='HTML', reply_markup=inline_message)


async def add_new_user_attitude_name(query: types.CallbackQuery, state: FSMContext):
    await FSMStateAddAttitude.state_new_attitude_name.set()
    message = await bot.send_message(chat_id=query.message.chat.id, text=ADD_ATTITUDE_MSG_1)
    message_id = message.message_id
    async with state.proxy() as data:
        data['inline_msg'] = query.message.message_id
        data['remove_msgs'] = [message_id]


async def add_new_user_attitude_sphere(message: types.Message, state: FSMContext):
    await FSMStateAddAttitude.state_new_attitude_sphere.set()
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Финансовую')],
        [types.KeyboardButton(text='Уверенность')],
        [types.KeyboardButton(text='Здоровье')]
    ], resize_keyboard=True)
    message_from_bot = await message.answer(text=ADD_ATTITUDE_MSG_2, reply_markup=keyboard)
    message_from_bot_id = message_from_bot.message_id
    async with state.proxy() as data:
        data['remove_msgs'].append(message_from_bot_id)
        data['remove_msgs'].append(message.message_id)
        data['Название установки'] = message.text


async def add_new_user_attitude_reminder(message: types.Message, state: FSMContext):
    await FSMStateAddAttitude.state_new_attitude_reminder.set()
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Утром')],
        [types.KeyboardButton(text='Днем')],
        [types.KeyboardButton(text='Вечером')],
        [types.KeyboardButton(text='Не напоминать')]
    ], resize_keyboard=True)
    message_from_bot = await message.answer(text=ADD_ATTITUDE_MSG_3, reply_markup=keyboard)
    message_from_bot_id = message_from_bot.message_id
    async with state.proxy() as data:
        data['remove_msgs'].append(message_from_bot_id)
        data['remove_msgs'].append(message.message_id)
        data['Сфера'] = message.text


async def save_new_user_attitude(message: types.Message, state=FSMContext):
    users_data = json.load(open(preferences_path, 'r'))
    user_id = str(message.from_user.id)
    chat_id = message.chat.id
    async with state.proxy() as data:
        new_attitude = {
            'Название установки': data['Название установки'],
            'Сфера': data['Сфера'],
            'Напоминать': message.text
        }
        users_data[user_id]['Установки'].append(new_attitude)
        json.dump(users_data, open(preferences_path, 'w'),
                  ensure_ascii=False, indent=3)

    user_attitudes = users_data[user_id]['Установки']
    current_attitude = 0
    last_attitude = len(user_attitudes) - 1

    inline_message = types.InlineKeyboardMarkup(row_width=1)

    left_arrow_data = arrow_callback_data.new(type='arrow', direction='left', next=str(last_attitude))
    right_arrow_data = arrow_callback_data.new(type='arrow', direction='right', next='1')
    remove_data = control_callback_data.new(type='control', action='remove', btn_num=current_attitude)
    append_data = control_callback_data.new(type='control', action='append', btn_num=current_attitude)

    inline_message.row(types.InlineKeyboardButton(text='<', callback_data=left_arrow_data),
                       types.InlineKeyboardButton(text='>', callback_data=right_arrow_data))
    inline_message.add(types.InlineKeyboardButton(text='Удалить', callback_data=remove_data))
    inline_message.add(types.InlineKeyboardButton(text='Добавить новую', callback_data=append_data))

    # attitude_name = user_attitudes[current_attitude]['Название установки']
    # attitude_sphere = user_attitudes[current_attitude]['Сфера']
    # attitude_reminder = user_attitudes[current_attitude]['Напоминать']
    # formatted_msg = ATTITUDE_INFO_TEMPLATE.format(attitude_name=attitude_name, attitude_sphere=attitude_sphere, attitude_reminder=attitude_reminder)

    tasks = []
    messages_to_remove = data['remove_msgs'] + [message.message_id]
    for elem in messages_to_remove:
        task = asyncio.create_task(bot.delete_message(chat_id=message.chat.id, message_id=int(elem)))
        tasks.append(task)
    await asyncio.gather(*tasks)
    # await bot.edit_message_text(text=formatted_msg, chat_id=chat_id,
    #                             message_id=data['inline_msg'], parse_mode='HTML', reply_markup=inline_message)
    await state.finish()


def register_my_attitudes_handlers(dp: Dispatcher):
    dp.register_message_handler(show_user_attitude, Text('Мои установки'))
    dp.register_callback_query_handler(show_previous_user_attitude, arrow_callback_data.filter(type='arrow', direction='left'))
    dp.register_callback_query_handler(show_next_user_attitude, arrow_callback_data.filter(type='arrow', direction='right'))
    dp.register_callback_query_handler(show_empty_user_attitudes, arrow_callback_data.filter(type='arrow', next='null'))
    dp.register_callback_query_handler(remove_user_attitude, control_callback_data.filter(type='control', action='remove'))
    dp.register_callback_query_handler(add_new_user_attitude_name, control_callback_data.filter(type='control', action='append'), state=None)
    dp.register_message_handler(add_new_user_attitude_sphere, state=FSMStateAddAttitude.state_new_attitude_name)
    dp.register_message_handler(add_new_user_attitude_reminder, Text(['Финансовую', 'Уверенность', 'Здоровье']), state=FSMStateAddAttitude.state_new_attitude_sphere)
    dp.register_message_handler(save_new_user_attitude, Text(['Утром', 'Днем', 'Вечером', 'Не напоминать']), state=FSMStateAddAttitude.state_new_attitude_reminder)