from bot.filters.custom_filters import NotCommand
from bot.init_bot import bot

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMStateFeedback(StatesGroup):
    state_start_feedback = State()


async def start_get_user_feedback(message: types.Message):
    await FSMStateFeedback.state_start_feedback.set()
    await message.answer(text='Напишите свой отзыв или пожелание')


async def end_get_user_feedback(message: types.Message, state: FSMContext):
    feedback_group_id = '-1001868511126'
    await bot.forward_message(chat_id=feedback_group_id, from_chat_id=message.chat.id, message_id=message.message_id)
    await message.answer(text='Спасибо за ваши пожелания, мы их обязательно учтем')
    await state.finish()


def register_feedback_handlers(dp: Dispatcher):
    dp.register_message_handler(start_get_user_feedback, commands='feedback', state=None)
    dp.register_message_handler(NotCommand(), state=FSMStateFeedback.state_start_feedback)
