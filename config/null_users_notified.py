import json
import os
import pdb

if __name__ == '__main__':
    path_to_preferences = os.path.dirname(__file__) + '/user_preferences.json'
    users_data = json.load(open(path_to_preferences, 'r'))
    for user, data in users_data.items():
        if data.get('Был оповещен сегодня') == 'Да' or \
           data.get('Был оповещен сегодня') == None:
            users_data[user]['Был оповещен сегодня'] = 'Нет'
        if data.get('Текущий пробный день') == '':
            users_data[user]['Текущий пробный день'] = '0'
    json.dump(users_data, open(path_to_preferences, 'w'), ensure_ascii=False, indent=4)
