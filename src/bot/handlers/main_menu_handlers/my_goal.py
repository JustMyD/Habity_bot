import json
import os

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot.init_bot import bot

preferences_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../config/user_preferences.json'))

goal_callback_data = CallbackData('goal', 'menu', 'action')


class FSMStateChangeGoal(StatesGroup):
    state_change_user_goal = State()


async def show_user_goal(message: types.Message):
    user_data = json.load(open(preferences_path, 'r'))
    user_goal = user_data[str(message.from_user.id)]['Цель']
    inline_message = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='Изменить цель', callback_data=goal_callback_data.new(menu='goal', action='change'))]
    ])
    await message.answer(text=f'Ваша текущая цель:\n{user_goal}', reply_markup=inline_message)


async def change_user_goal(query: types.CallbackQuery, state: FSMContext):
    await FSMStateChangeGoal.state_change_user_goal.set()
    message_from_bot = await query.message.answer(text='Введите свою новую цель')
    message_from_bot_id = message_from_bot.message_id
    async with state.proxy() as data:
        data['inline_msg'] = query.message.message_id
        data['delete_msg'] = message_from_bot_id


async def get_new_user_goal(message: types.Message, state: FSMContext):
    user_data = json.load(open(preferences_path, 'r'))
    user_data[str(message.from_user.id)]['Цель'] = message.text
    json.dump(user_data, open(preferences_path, 'w'), ensure_ascii=False, indent=3)
    inline_message = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='Изменить цель',
                                    callback_data=goal_callback_data.new(menu='goal', action='change'))]
    ])
    async with state.proxy() as data:
        await bot.delete_message(chat_id=message.chat.id, message_id=data['delete_msg'])
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await bot.edit_message_text(text=f'Ваша текущая цель:\n{message.text}', chat_id=message.chat.id,
                                    message_id=data['inline_msg'], reply_markup=inline_message)
    await state.finish()


def register_my_goal_handlers(dp: Dispatcher):
    dp.register_message_handler(show_user_goal, Text('Моя цель'))
    dp.register_callback_query_handler(change_user_goal, goal_callback_data.filter(menu='goal', action='change'), state=None)
    dp.register_message_handler(get_new_user_goal, state=FSMStateChangeGoal.state_change_user_goal)
