import json

if __name__ == '__main__':
    file = json.load(open('../../config/user_preferences.json', 'r'))
    print(file)