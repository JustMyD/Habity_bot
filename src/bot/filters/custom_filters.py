from aiogram.dispatcher.filters import BoundFilter
from aiogram import types


class NotCommand(BoundFilter):
    async def check(self, message: types.Message):
        result = '/' not in message.text
        return result


#class NotPrivate(BoundFilter):
#    async def check(self, message: types.Message):
#        return message.chat.type != types.ChatType.PRIVATE
