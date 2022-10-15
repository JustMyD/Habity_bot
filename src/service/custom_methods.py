import json

import requests
import os
import logging
from dotenv import load_dotenv
from aiogram import types
from babel.support import LazyProxy
import datetime

load_dotenv()
logs_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../logs/habity_logger.log'))

logging.basicConfig(filename=logs_path, format='%(asctime)s | %(levelname)s: %(message)s', level=logging.INFO)


def _normalize(obj):
    """
    Normalize dicts and lists

    :param obj:
    :return: normalized object
    """
    if isinstance(obj, list):
        return [_normalize(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: _normalize(v) for k, v in obj.items() if v is not None}
    elif hasattr(obj, 'to_python'):
        return obj.to_python()
    return obj


def prepare_arg(value):
    """
    Stringify dicts/lists and convert datetime/timedelta to unix-time

    :param value:
    :return:
    """
    if value is None:
        return value
    if isinstance(value, (list, dict)) or hasattr(value, 'to_python'):
        return json.dumps(_normalize(value))
    if isinstance(value, datetime.timedelta):
        now = datetime.datetime.now()
        return int((now + value).timestamp())
    if isinstance(value, datetime.datetime):
        return round(value.timestamp())
    if isinstance(value, LazyProxy):
        return str(value)
    return value


async def send_message(chat_id: str, text: str, **kwargs):
    """
    Метод отправки сообщения на сервер телеграмм.
    chat_id и message_text обязательные параметры.
    В kwargs можно указать дополнительные не обязательные параметры:

    parse_mode               -  Использование разметки в сообщении         ('Markdown', 'MarkdownV2', 'HTML')
    entities                 -  Прямые включения в сообщения               (ожидается json-словарь)
    disable_web_page_preview -  Отключить предпросмотр ссылок              (Bool)
    disable_notification     -  Отключить оповещение для сообщения         (Bool)
    protect_content          -  Запретить пересылку и сохранение сообщения (Bool)
    reply_markup             -  Доп клавиатуры                             (InlineKeyboardMarkup,
                                                                            ReplyKeaboardMarkup,
                                                                            ReplyKeyboardRemove,
                                                                            ForceReply)
    :param chat_id: Id чата пользователя (обязательный)
    :param text: Текст сообщения (обязательный)
    :param kwargs: Не обязательные параметры
    :return:
    """
    token = os.getenv('API_TOKEN')
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    json_data = {
        'chat_id': chat_id,
        'text': text
    }
    for k, v in kwargs.items():
        if k == 'reply_markup':
            v = prepare_arg(v)
        json_data.update({k: v})
    try:
        response = requests.post(url, data=json_data)
        logging.info(f'Message: {text}')
    except Exception as e:
        logging.error(f'Chat_id {chat_id} - message was not sent with error: {e}')


if __name__ == '__main__':
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Test button')]
    ], resize_keyboard=True)
    send_message('1823068761', 'test', reply_markup=keyboard)
