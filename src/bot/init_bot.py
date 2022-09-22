import json
import os

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

from .const import DAY_0_MSG_1, DAY_0_MSG_2, USER_GOAL_MSG_1, USER_GOAL_MSG_2, USER_GOAL_MSG_3

load_dotenv()

bot = Bot(token=os.getenv('API_TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class FSMStateGoal(StatesGroup):
    state_first_message = State()
    state_second_message = State()
    state_third_message = State()


# 0 День Начало
@dp.message_handler(commands='start')
async def intro_message(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text='Определить цель'))
    await message.answer(text=DAY_0_MSG_1, reply_markup=keyboard)


@dp.message_handler(Text('Определить цель'), state=None)
async def start_get_user_goal(message: types.Message):
    await FSMStateGoal.state_first_message.set()
    await message.answer(text=USER_GOAL_MSG_1, reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=FSMStateGoal.state_first_message)
async def get_user_goal(message: types.Message):
    await FSMStateGoal.state_second_message.set()
    await message.answer(text=USER_GOAL_MSG_2)


@dp.message_handler(state=FSMStateGoal.state_second_message)
async def get_user_goal_date(message: types.Message, state: FSMContext):
    await FSMStateGoal.state_third_message.set()
    await message.answer(text=USER_GOAL_MSG_3)


@dp.message_handler(state=FSMStateGoal.state_third_message)
async def get_user_goal_reason(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Утром')],
        [types.KeyboardButton(text='Днем')],
        [types.KeyboardButton(text='Вечером')]
    ], resize_keyboard=True)
    await message.answer(text=DAY_0_MSG_2, reply_markup=keyboard)
    await state.finish()


@dp.message_handler(Text('Утром') or Text('Днем') or Text('Вечером'))
async def zeroday_last_message(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_preferences = json.load(open('config/user_preferences.json', 'r'))
    user_data = user_preferences.get(user_id)
    if not user_data:
        user_preferences[user_id] = dict()
    user_preferences[user_id]['Chat_id'] = chat_id
    user_preferences[user_id]['Время отправки сообщений'] = message.text
    user_preferences[user_id]['Текущий день'] = '0'
    json.dump(user_preferences, open('config/user_preferences.json', 'w'), indent=3, ensure_ascii=False)
    await message.answer(text='Отлично, мы с тобой определили цель, зачем она тебе и в какие сроки ты хочешь ее достичь. До завтра!', reply_markup=types.ReplyKeyboardRemove())


# 0 День Конец


# 1 День Начало
# async def get_user_habits():
#     await bot.send_message(chat_id='', text='')
