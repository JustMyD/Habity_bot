from aiogram.dispatcher.filters import BoundFilter
from aiogram import types


class NotCommand(BoundFilter):
    async def check(self, message: types.Message):
        return '/' not in message.text


#class NotPrivate(BoundFilter):
#    async def check(self, message: types.Message):
#        return message.chat.type != types.ChatType.PRIVATE
