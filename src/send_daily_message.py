"""
Вызываем с помощью CronTab для рассылки сообщений пользователям 3 раза в день
"""
import json
from datetime import datetime
import os
import logging

import asyncio
from bot.init_bot import INIT_DAY_FUNCTIONS
logging.basicConfig(filename='/home/www/Bot_projects/Habity_bot/src/logger.log',
                    encoding='utf-8',
                    format='%(threadName)s %(name)s %(levelname)s: %(message)s',
                    level=logging.INFO)


def check_current_timeinterval() -> str:
    """
    Определить текущий временной промежуток
    :return:
    """
    current_day_time = datetime.now().strftime('%H')
    timeinterval = ''
    if 6 < int(current_day_time) < 9:
        timeinterval = 'Утром'
    elif 12 < int(current_day_time) < 14:
        timeinterval = 'Днем'
    elif 18 < int(current_day_time) < 20:
        timeinterval = 'Вечером'

    return timeinterval


def get_users_for_mailing(interval: str) -> list:
    """
    Парсим конфиг для получения списка пользователей и текущего дня пользователя для рассылки сообщений
    :return:
    """
    users_data = json.load(open('config/user_preferences.json', 'r'))
    mailing_list = []
    for user, data in users_data.items():
        if data['Время отправки сообщений'] == interval and int(data['Текущий пробный день']) < 6 and data['Был оповещен сегодня'] == 'Нет' or int(data['Текущий пробный день']) == 0:
            mailing_list.append((user, data['Текущий пробный день']))
    return mailing_list


def send_messages(mailing_list: list):
    """
    Разослать сообщения пользователям в зависимости от текущего временного промежутка и дня
    :return:
    """
    io_loop = asyncio.get_event_loop()
    bot_tasks = set()
    for user_data in mailing_list:
        user_id = user_data[0]
        current_day = user_data[1]
        task = io_loop.create_task(INIT_DAY_FUNCTIONS[current_day](user_id))
        bot_tasks.add(task)
        task.add_done_callback(bot_tasks.discard)
    logging.info(f'Current tasks is: {bot_tasks}')
    try:
        logging.info('Start running tasks')
        io_loop.run_until_complete(asyncio.wait(bot_tasks))
        logging.info('End running tasks')
    except Exception as e:
        logging.error(e)
    io_loop.close()


def main():
    timeinterval = check_current_timeinterval()
    mailing_list = get_users_for_mailing(timeinterval)
    send_messages(mailing_list)


if __name__ == '__main__':
    main()
