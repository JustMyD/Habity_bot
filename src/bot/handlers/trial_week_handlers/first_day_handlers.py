from bot.init_bot import bot, INIT_DAY_FUNCTIONS
from bot.const.msgs import DAY_1_INTRO_MSG, DAY_1_MSG_1, USER_HABIT_MSG_1, USER_HABIT_MSG_2, USER_HABIT_MSG_3, DAY_1_MSG_2
from service.custom_methods import send_message

import json
import os

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

preferences_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../config/user_preferences.json'))


class FSMStateTrialHabbit(StatesGroup):
    state_habbit_name = State()
    state_habbit_trigger = State()
    state_habbit_value = State()


async def first_day_intro(user_id: str):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text='Отправить привычку'))
    user_data = json.load(open(preferences_path, 'r'))
    user_data[user_id]['Был оповещен сегодня'] = 'Да'
    json.dump(user_data, open(preferences_path, 'w'), ensure_ascii=False, indent=3)
    await send_message(chat_id=user_id, text=DAY_1_INTRO_MSG, reply_markup=types.ReplyKeyboardRemove())
    await send_message(chat_id=user_id, text=DAY_1_MSG_1, reply_markup=keyboard)


async def trial_time_habbit_name(message: types.Message):
    await FSMStateTrialHabbit.state_habbit_name.set()
    await message.answer(text=USER_HABBIT_MSG_1, reply_markup=types.ReplyKeyboardRemove())


async def trial_time_habbit_trigger(message: types.Message, state: FSMContext):
    await FSMStateTrialHabbit.state_habbit_trigger.set()
    async with state.proxy() as data:
        data['Название привычки'] = message.text
    await message.answer(text=USER_HABBIT_MSG_2)


async def trial_time_habbit_value(message: types.Message, state: FSMContext):
    await FSMStateTrialHabbit.state_habbit_value.set()
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Да')],
        [types.KeyboardButton(text='Нет')]
    ], resize_keyboard=True)
    async with state.proxy() as data:
        data['Триггер привычки'] = message.text
    await message.answer(text=USER_HABBIT_MSG_3, reply_markup=keyboard)


async def first_day_last_message(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Отправить привычку')],
        [types.KeyboardButton(text='Изменить цель')]
    ])
    user_data = json.load(open(preferences_path, 'r'))
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
        user_data[user_id]['Текущий пробный день'] = '2'
        json.dump(user_data, open(preferences_path, 'w'), ensure_ascii=False, indent=3)
    await message.answer(text=DAY_1_MSG_2.format(user_goal=user_goal, goal_date=goal_date, goal_reason=goal_reason),
                         reply_markup=keyboard)
    await state.finish()


def register_handlers_first_day(dp: Dispatcher):
    dp.register_message_handler(trial_time_habbit_name, Text(['Отправить привычку']), state=None)
    dp.register_message_handler(trial_time_habbit_trigger, state=FSMStateTrialHabbit.state_habbit_name)
    dp.register_message_handler(trial_time_habbit_value, state=FSMStateTrialHabbit.state_habbit_trigger)
    dp.register_message_handler(first_day_last_message, Text(['Да', 'Нет']),
                                state=FSMStateTrialHabbit.state_habbit_value)


INIT_DAY_FUNCTIONS.update({'1': first_day_intro})
