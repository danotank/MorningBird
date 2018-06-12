import time
import vk_api
import json
import requests
import random
vk_public = vk_api.VkApi(token = '6ae53ccd3d9cb5ddc2601d9079fd72496640218b5f593378ce47b4783e46c278fed1f8f5571811a640b5d')

#login = input()
#password = input()
#vk = vk_api.VkApi(login, password)
vk_user = vk_api.VkApi('vasilisa.bo4arova@yandex.ru', 'fake1488')
try:
    vk_user.auth()
except vk_api.AuthError as ex_message:
    print(ex_message)


WeatherAppId = "8ebb2eb2da40cb332bd20218af751a90"
values = {'out': 0,'count': 100,'time_offset': 60}

def write_msg(user_id, s):
    vk_public.method('messages.send', {'user_id':user_id,'message':s})

def send_pic(user_id, pic):
    vk_public.method('messages.send', {'user_id':user_id, 'attachment': pic})

def get_weather(reminders):
    umbrella = False
    city_id = 524901
    res = requests.get("http://api.openweathermap.org/data/2.5/forecast", params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': WeatherAppId})
    data = res.json()
    weather = 'Погода: '
    for i in data['list']:
        dt = str(int(i['dt_txt'].split()[1].strip('0').split(':')[0]) + 3)
        if dt == '24':
            dt = 'полночь'
        weather += '\n' + 'В ' + dt + ' будет ' + '{0:+3.0f}'.format(i['main']['temp']) + ' и ' + i['weather'][0]['description']
        if 'дождь' in i['weather'][0]['description']:
            umbrella = True
        if dt == 'полночь':
            if umbrella:
                reminders[str(item['user_id'])].append('Не забудь взять зонтик!')
            return weather, reminders


def get_reminders():
    with open("data.json", "r") as f:
        s = f.read()
    r = json.loads(s)
    return r

mems = vk_user.method('photos.get', {'owner_id':-167413779, 'album_id':254617947})

reminders=get_reminders()
while True:
    response = vk_public.method('messages.get', values)
    if response['items']:
        values['last_message_id'] = response['items'][0]['id']
    for item in response['items']:
        if str.lower(item["body"])=='напоминание':
            write_msg(item['user_id'],'А какой текст?')
            response = vk_public.method('messages.get', values)
            while not response['items']:
                response = vk_public.method('messages.get', values)
                if response['items']:
                    break
                time.sleep(1)
            if response['items']:
                message = response['items'][0]
                values['last_message_id'] = message['id']
                if not str(item['user_id']) in reminders.keys():
                    reminders[str(item['user_id'])] = []
                reminders[str(item['user_id'])].append(message['body'])
                with open('data.json', 'w') as file:
                    json.dump(reminders, file)
                write_msg(item['user_id'], message['body'])
        else:
            weather, reminders = get_weather(reminders)
            r_mem = random.choice(mems['items'])
            attachment = 'photo' + '-167413779_' + str(r_mem['id'])
            send_pic(item['user_id'], attachment )
            write_msg(item['user_id'], weather)
            for reminder in reminders[str(item['user_id'])]:
                write_msg(item['user_id'], reminder)
            reminders[str(item['user_id'])] = []
            with open('data.json', 'w') as file:
                json.dump(reminders, file)
        time.sleep(1)
