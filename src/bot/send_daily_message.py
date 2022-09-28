"""
Вызываем с помощью CronTab для рассылки сообщений пользователям 3 раза в день
"""
from init_bot import bot
import asyncio


def check_current_timeinterval():
    """
    Определить текущий временной промежуток
    :return:
    """
    pass


def parse_preferences():
    """
    Парсим настройки пользователей, для рассылки по текущему временному промежутку
    :return:
    """
    pass


async def mailing_list():
    """
    Разослать сообщения пользователям в зависимости от текущего временного промежутка
    :return:
    """
    await bot.send_message(chat_id='1823068761', text='test')


if __name__ == '__main__':
    asyncio.run(mailing_list())
