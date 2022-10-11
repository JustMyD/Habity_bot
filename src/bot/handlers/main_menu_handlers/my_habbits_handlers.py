from aiogram import Dispatcher, types 
from aiogram.dispatcher.filters import Text
from aiogram.utils.callback_data import CallbackData

arrows_callback_data = CallbackData('controlling', 'direction')



#def categories_main_menu(categories: list, category_menu: str) -> types.InlineKeyboardMarkup:
#    inline_message = types.InlineKeyboardMarkup(row_width=1)
#    for category in categories:
#        inline_message.insert(types.InlineKeyboardButton(text=f'{category}',
#                                                         callback_data=callback_data['category'].new(category_menu, 'show', category)))
#    if category_menu != 'main_menu':
#        inline_message.insert(types.InlineKeyboardButton(text='Добавить категорию',
#                                                         callback_data=callback_data['category'].new(category_menu, 'add', 'new')))
#
#    return inline_message
#


# @dp.message_handler(Text('Мои привычки'))
async def show_user_habbits(message: types.Message):
    #inline_message = types.InlineKeyboardMarkup(keyboard=[
    #    [
    #        [types.InlineKeyboardButton(text='<', callback_data=arrows_callback_data.new('left')],
    #        [types.InlineKeyboardButton(text='>', callback_data=arrows_callback_data.new('right')]
    #    ]
    #],row_width=1)
    await message.answer(text='test')
    


def register_my_habbits_handlers(dp: Dispatcher):
    dp.register_message_handler(show_user_habbits, Text('Мои привычки'))
