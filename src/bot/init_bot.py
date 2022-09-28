"""
Пока все колбэки здесь в одной куче, нужно раскидать TrialDays функции по отдельным скриптам, в init скрипте
остаются основные колбэки
"""
import json
import os
import time

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.callback_data import CallbackData
from dotenv import load_dotenv

from .const import DAY_0_INTRO_MSG, DAY_0_MSG_1, DAY_0_MSG_2, USER_GOAL_MSG_1, USER_GOAL_MSG_2, USER_GOAL_MSG_3, DAY_0_MSG_3
from .const import DAY_1_INTRO_MSG, DAY_1_MSG_1, USER_HABBIT_MSG_1, USER_HABBIT_MSG_2, USER_HABBIT_MSG_3, DAY_1_MSG_2
from .const import DAY_2_INTRO_MSG, DAY_2_MSG_1, USER_ATTITUDE_MSG_1, USER_ATTITUDE_MSG_2, DAY_2_MSG_2
from .const import DAY_3_INTRO_MSG, DAY_3_MSG_1, USER_CHARACTERISTIC_1, USER_CHARACTERISTIC_2, DAY_3_MSG_2
from .const import DAY_4_INTRO_MSG, DAY_4_MSG_1, DAY_4_MSG_2, DAY_4_MSG_3, DAY_4_MSG_4, DAY_4_MSG_5
from .const import DAY_5_INTRO_MSG, DAY_5_MSG_1, DAY_5_MSG_2, DAY_5_MSG_3, DAY_5_MSG_4

load_dotenv()

bot = Bot(token=os.getenv('API_TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class FSMStateGoal(StatesGroup):
    state_first_message = State()
    state_second_message = State()
    state_third_message = State()
    state_fourth_message = State()


# 0 День Начало
@dp.message_handler(commands='start')
async def intro_message(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text='Определить цель'))
    user_data = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    user_id = str(message.from_user.id)
    if user_id not in user_data.keys():
        user_data[user_id] = {
            "Обращение": "",
            "Цель": "",
            "Срок цели": "",
            "Зачем цель": "",
            "Привычки": [],
            "Установки": [],
            "Напоминать об установках": "",
            "Характеристики": [],
            "Chat_id": "",
            "Время отправки сообщений": "",
            "Текущий пробный день": ""
        }
        json.dump(user_data, open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'w'), ensure_ascii=False, indent=3)
    await message.answer(text=DAY_0_INTRO_MSG)
    time.sleep(1)
    await message.answer(text=DAY_0_MSG_1, reply_markup=keyboard)


@dp.message_handler(Text('Определить цель'), state=None)
async def start_get_user_goal(message: types.Message):
    await FSMStateGoal.state_first_message.set()
    await message.answer(text=USER_GOAL_MSG_1, reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=FSMStateGoal.state_first_message)
async def get_user_goal(message: types.Message, state=FSMContext):
    await FSMStateGoal.state_second_message.set()
    async with state.proxy() as data:
        data['Цель'] = message.text
    await message.answer(text=USER_GOAL_MSG_2)


@dp.message_handler(state=FSMStateGoal.state_second_message)
async def get_user_goal_date(message: types.Message, state: FSMContext):
    await FSMStateGoal.state_third_message.set()
    async with state.proxy() as data:
        data['Срок цели'] = message.text
    await message.answer(text=USER_GOAL_MSG_3)


@dp.message_handler(state=FSMStateGoal.state_third_message)
async def get_user_goal_reason(message: types.Message, state: FSMContext):
    await FSMStateGoal.state_fourth_message.set()
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Утром')],
        [types.KeyboardButton(text='Днем')],
        [types.KeyboardButton(text='Вечером')]
    ], resize_keyboard=True)
    async with state.proxy() as data:
        data['Зачем цель'] = message.text
    await message.answer(text=DAY_0_MSG_2, reply_markup=keyboard)


@dp.message_handler(Text(['Утром', 'Днем', 'Вечером']), state=FSMStateGoal.state_fourth_message)
async def zeroday_last_message(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    chat_id = message.chat.id
    user_preferences = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    if str(user_id) not in user_preferences.keys():
        user_preferences[user_id] = {}
    async with state.proxy() as data:
        user_preferences[user_id]['Цель'] = data['Цель']
        user_preferences[user_id]['Срок цели'] = data['Срок цели']
        user_preferences[user_id]['Зачем цель'] = data['Зачем цель']
    user_preferences[user_id]['Chat_id'] = chat_id
    user_preferences[user_id]['Время отправки сообщений'] = message.text
    user_preferences[user_id]['Текущий пробный день'] = '0'
    json.dump(user_preferences, open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'w'),
              ensure_ascii=False, indent=3)
    await message.answer(text=DAY_0_MSG_3, reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


# 0 День Конец


# 1 День Начало

class FSMStateHabbit(StatesGroup):
    state_first_message = State()
    state_second_message = State()
    state_third_message = State()
    state_fourth_message = State()


# @dp.message_handler(Text('Начать первый день'))
async def first_day_intro(user_id: str):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text='Отправить привычку'))
    user_data = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    user_data[user_id]['Текущий пробный день'] = '1'
    json.dump(user_data, open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'w'), ensure_ascii=False, indent=3)
    await bot.send_message(chat_id=user_id, text=DAY_1_INTRO_MSG, reply_markup=types.ReplyKeyboardRemove())
    time.sleep(1)
    await bot.send_message(chat_id=user_id, text=DAY_1_MSG_1, reply_markup=keyboard)


@dp.message_handler(Text(['Отправить привычку', '/add_habit']), state=None)
async def get_user_habbit_name(message: types.Message):
    await FSMStateHabbit.state_first_message.set()
    await message.answer(text=USER_HABBIT_MSG_1, reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=FSMStateHabbit.state_first_message)
async def get_user_habbit_trigger(message: types.Message, state: FSMContext):
    await FSMStateHabbit.state_second_message.set()
    async with state.proxy() as data:
        data['Название привычки'] = message.text
    await message.answer(text=USER_HABBIT_MSG_2)


@dp.message_handler(state=FSMStateHabbit.state_second_message)
async def get_user_habbit_value(message: types.Message, state: FSMContext):
    await FSMStateHabbit.state_third_message.set()
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Да')],
        [types.KeyboardButton(text='Нет')]
    ], resize_keyboard=True)
    async with state.proxy() as data:
        data['Триггер привычки'] = message.text
    await message.answer(text=USER_HABBIT_MSG_3, reply_markup=keyboard)


@dp.message_handler(Text(['Да', 'Нет']), state=FSMStateHabbit.state_third_message)
async def first_day_last_message(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Отправить привычку')],
        [types.KeyboardButton(text='Изменить цель')]
    ])
    user_data = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    user_id = str(message.from_user.id)
    user_goal = user_data[user_id]['Цель']
    goal_date = user_data[user_id]['Срок цели']
    goal_reason = user_data[user_id]['Зачем цель']
    async with state.proxy() as data:
        new_habit = {
            'Название привычки': data['Название привычки'],
            'Триггер': data['Триггер привычки'],
            'Полезна?': message.text
        }
        user_data[user_id]['Привычки'].append(new_habit)
        json.dump(user_data, open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'w'), ensure_ascii=False, indent=3)
    await message.answer(text=DAY_1_MSG_2.format(user_goal=user_goal, goal_date=goal_date, goal_reason=goal_reason),
                         reply_markup=keyboard)
    await state.finish()


# 1 День конец


# ToDo CallbackQuery для списка целей с возможностью изменения цели или ее удаления
@dp.message_handler(Text('Изменить цель'))
async def change_user_goal(query: types.CallbackQuery):
    pass


@dp.message_handler(Text('Удалить цель'))
async def delete_user_goal(query: types.CallbackQuery):
    pass


# 2 День начало

class FSMStateAttitude(StatesGroup):
    state_first_message = State()
    state_second_message = State()


# @dp.message_handler(Text('Начать второй день'))
async def second_day_intro(user_id: str):
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Отправить установку')]
    ], resize_keyboard=True)
    user_data = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    user_data[user_id]['Текущий пробный день'] = '2'
    json.dump(user_data, open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'w'), ensure_ascii=False, indent=3)
    await bot.send_message(chat_id=user_id, text=DAY_2_INTRO_MSG, reply_markup=types.ReplyKeyboardRemove())
    time.sleep(1)
    await bot.send_message(chat_id=user_id, text=DAY_2_MSG_1, reply_markup=keyboard)


@dp.message_handler(Text('Отправить установку'), state=None)
async def get_user_attitude_name(message: types.Message):
    await FSMStateAttitude.state_first_message.set()
    await message.answer(text=USER_ATTITUDE_MSG_1, reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=FSMStateAttitude.state_first_message)
async def get_user_attitude_value(message: types.Message, state: FSMContext):
    await FSMStateAttitude.state_second_message.set()
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Да')],
        [types.KeyboardButton(text='Нет')]
    ], resize_keyboard=True)
    async with state.proxy() as data:
        data['Название установки'] = message.text
    await message.answer(text=USER_ATTITUDE_MSG_2, reply_markup=keyboard)


@dp.message_handler(Text(['Да', 'Нет']), state=FSMStateAttitude.state_second_message)
async def second_day_last_message(message: types.Message, state: FSMContext):
    user_data = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    user_id = str(message.from_user.id)
    async with state.proxy() as data:
        new_attitude = {
            'Название установки': data['Название установки'],
            'Полезна?': message.text
        }
        user_data[user_id]['Установки'].append(new_attitude)
        json.dump(user_data, open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'w'), ensure_ascii=False, indent=3)
    await message.answer(text=DAY_2_MSG_2, reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


# 2 День конец


# 3 День начало

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

    user_data[user_id]['Текущий пробный день'] = '3'
    json.dump(user_data, open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'w'), ensure_ascii=False, indent=3)
    await bot.send_message(chat_id=user_id, text=DAY_3_INTRO_MSG, reply_markup=types.ReplyKeyboardRemove())
    time.sleep(1)
    await bot.send_message(chat_id=user_id, text=DAY_3_MSG_1.format(user_goal=user_goal, goal_reason=goal_reason), reply_markup=keyboard)


@dp.message_handler(Text('Отправить характеристику'), state=None)
async def get_user_characteristic_name(message: types.Message):
    await FSMStateCharacteristic.state_first_message.set()
    await message.answer(text=USER_CHARACTERISTIC_1, reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=FSMStateCharacteristic.state_first_message)
async def get_user_characteristic_value(message: types.Message, state: FSMContext):
    await FSMStateCharacteristic.state_second_message.set()
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Да')],
        [types.KeyboardButton(text='Нет')]
    ], resize_keyboard=True)
    async with state.proxy() as data:
        data['Название характеристики'] = message.text
    await message.answer(text=USER_CHARACTERISTIC_2, reply_markup=keyboard)


@dp.message_handler(Text(['Да', 'Нет']), state=FSMStateCharacteristic.state_second_message)
async def third_day_last_message(message: types.Message, state: FSMContext):
    user_data = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    user_id = str(message.from_user.id)
    async with state.proxy() as data:
        new_characteristic = {
            'Название характеристики': data['Название характеристики'],
            'Позитивная?': message.text
        }
        user_data[user_id]['Характеристики'].append(new_characteristic)
        json.dump(user_data, open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'w'), ensure_ascii=False, indent=3)
    await message.answer(text=DAY_3_MSG_2, reply_markup=types.ReplyKeyboardRemove())
    await state.finish()

# 3 День конец


# 4 День начало

class FSMFourthDay(StatesGroup):
    state_first_message = State()
    # state_second_message = State()


characteristic_callback_data = CallbackData('characteristic', 'name', 'action')


# @dp.message_handler(Text('Начать четвертый день'), state=None)
async def fourth_day_intro(user_id: str):
    await bot.send_message(chat_id=user_id, text=DAY_4_INTRO_MSG, reply_markup=types.ReplyKeyboardRemove())
    time.sleep(1)
    await bot.send_message(chat_id=user_id, text=DAY_4_MSG_1)
    inline_message = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='Мистер', callback_data=characteristic_callback_data.new('Мистер', 'choose'))],
        [types.InlineKeyboardButton(text='Молодой человек', callback_data=characteristic_callback_data.new('Молодой человек', 'choose'))],
        [types.InlineKeyboardButton(text='Мисс', callback_data=characteristic_callback_data.new('Мисс', 'choose'))],
        [types.InlineKeyboardButton(text='Леди', callback_data=characteristic_callback_data.new('Леди', 'choose'))],
        [types.InlineKeyboardButton(text='Миссис', callback_data=characteristic_callback_data.new('Миссис', 'choose'))],
        [types.InlineKeyboardButton(text='Мадам', callback_data=characteristic_callback_data.new('Мадам', 'choose'))]
    ], row_width=1)
    user_data = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    user_data[user_id]['Текущий пробный день'] = '4'
    json.dump(user_data, open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'w'),
              ensure_ascii=False, indent=3)
    await bot.send_message(chat_id=user_id, text=DAY_4_MSG_2, reply_markup=inline_message)


@dp.callback_query_handler(characteristic_callback_data.filter(action='choose'), state=None)
async def get_new_user_characteristic(query: types.CallbackQuery):
    await FSMFourthDay.state_first_message.set()
    user_data = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    user_id = str(query.from_user.id)
    chat_id = str(query.message.chat.id)
    main_characteristic = query.data.split(':')[1]
    user_data[user_id]['Обращение'] = main_characteristic
    json.dump(user_data, open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'w'), ensure_ascii=False, indent=3)
    await query.answer(text=DAY_4_MSG_3.format(main_characteristic=main_characteristic), show_alert=True)
    await bot.send_message(chat_id=chat_id, text='(тут запускается алгоритм подбора характеристик')
    time.sleep(1)
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Да')]
    ], resize_keyboard= True)
    await bot.send_message(chat_id=chat_id, text=DAY_4_MSG_4, reply_markup=keyboard)


@dp.message_handler(Text('Да'), state=FSMFourthDay.state_first_message)
async def get_user_yes(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Отправить характеристику')],
        [types.KeyboardButton(text='Отправить установку')],
        [types.KeyboardButton(text='Отправить привычку')]
    ], resize_keyboard=True)
    await message.answer(text=DAY_4_MSG_5, reply_markup=keyboard)
    await state.finish()


# 4 День конец


# 5 День начало

class FSMFiveDay(StatesGroup):
    state_first_message = State()
    # state_second_message = State()


# @dp.message_handler(Text('Начать пятый день'), state=None)
async def fife_day_intro(user_id: str):
    await bot.send_message(chat_id=user_id, text=DAY_5_INTRO_MSG, reply_markup=types.ReplyKeyboardRemove())
    time.sleep(1)
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Финансовую')],
        [types.KeyboardButton(text='Уверенность')],
        [types.KeyboardButton(text='Здоровье')]
    ], resize_keyboard=True)
    user_data = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    main_characteristic = user_data[user_id]['Обращение']
    user_data[user_id]['Текущий пробный день'] = '5'
    json.dump(user_data, open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'w'), ensure_ascii=False, indent=3)
    await bot.send_message(chat_id=user_id, text=DAY_5_MSG_1.format(main_characteristic=main_characteristic), reply_markup=keyboard)


@dp.message_handler(Text(['Финансовую', 'Уверенность', 'Здоровье']), state=None)
async def get_user_sphere(message: types.Message):
    await FSMFiveDay.state_first_message.set()
    await message.answer(text=DAY_5_MSG_2, reply_markup=types.ReplyKeyboardRemove())
    await message.answer(text='(тут запускается алгоритм подбора установок')
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Да')],
        [types.KeyboardButton(text='Нет')]
    ], resize_keyboard=True)
    time.sleep(1)
    await message.answer(text=DAY_5_MSG_3, reply_markup=keyboard)


@dp.message_handler(Text(['Да', 'Нет']), state=FSMFiveDay.state_first_message)
async def get_user_reminder(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Отправить характеристику')],
        [types.KeyboardButton(text='Отправить установку')],
        [types.KeyboardButton(text='Отправить привычку')]
    ], resize_keyboard=True)
    user_data = json.load(open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'r'))
    user_id = str(message.from_user.id)
    user_data[user_id]['Напоминать об установках'] = message.text
    json.dump(user_data, open('/home/www/Bot_projects/Habity_bot/config/user_preferences.json', 'w'), ensure_ascii=False, indent=3)
    await message.answer(text=DAY_5_MSG_4, reply_markup=keyboard)
    await state.finish()


# 5 День конец


INIT_DAY_FUNSTIONS = {
    '1': first_day_intro,
    '2': second_day_intro,
    '3': third_day_intro,
    '4': fourth_day_intro,
    '5': fife_day_intro
}
