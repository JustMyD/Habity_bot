"""
Вызываем с помощью CronTab для рассылки сообщений пользователям 3 раза в день
"""
import json
import asyncio
import os
import logging
from datetime import datetime

# from bot.init_bot import INIT_DAY_FUNCTIONS
from bot.handlers.trial_week_handlers.zero_day_handlers import intro_message
from bot.handlers.trial_week_handlers.first_day_handlers import first_day_intro
from bot.handlers.trial_week_handlers.second_day_handlers import second_day_intro
from bot.handlers.trial_week_handlers.third_day_handlers import third_day_intro
from bot.handlers.trial_week_handlers.fourth_day_handlers import fourth_day_intro
from bot.handlers.trial_week_handlers.fifth_day_handlers import fifth_day_intro


logs_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'logs/daily_sender_logger.log'))

logging.basicConfig(filename=logs_path, encoding='utf-8', format='%(asctime)s | %(levelname)s: %(message)s', level=logging.INFO)

INIT_DAY_FUNCTIONS = {
    '0': intro_message,
    '1': first_day_intro,
    '2': second_day_intro,
    '3': third_day_intro,
    '4': fourth_day_intro,
    '5': fifth_day_intro
}


def check_current_timeinterval() -> str:
    """
    Определить текущий временной промежуток
    :return:
    """
    current_day_time = datetime.now().strftime('%H')
    timeinterval = ''
    if 6 < int(current_day_time) < 8:
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
        send_time = data.get('Время отправки сообщений', 'Утром')
        current_trial_day = int(data.get('Текущий пробный день'))
        already_notified = data.get('Был оповещен сегодня')
        if send_time == interval and current_trial_day < 6 and (already_notified == 'Нет' or current_trial_day == 0):
            mailing_list.append((user, data['Текущий пробный день']))
    return mailing_list


def send_messages(mailing_list: list):
    """
    Разослать сообщения пользователям в зависимости от текущего временного промежутка и дня
    :return:
    """
    io_loop = asyncio.get_event_loop()
    bot_tasks = set()
    logging.info(f'Task list: {mailing_list}')
    for user_data in mailing_list:
        user_id = user_data[0]
        current_day = user_data[1]
        task = io_loop.create_task(INIT_DAY_FUNCTIONS[current_day](user_id))
        bot_tasks.add(task)
        task.add_done_callback(bot_tasks.discard)
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
