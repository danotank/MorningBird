import time
import vk_api
import json
import requests
vk = vk_api.VkApi(token = '7d07fa9396f2a078727fa4faf6b505e6998fdc5a5e2a9f94c064e58674fd36c53da1c473c2affa4b8822b')
WeatherAppId = '8ebb2eb2da40cb332bd20218af751a90'
values = {'out': 0,'count': 100,'time_offset': 60}
def write_msg(user_id, s):
    vk.method('messages.send', {'user_id':user_id,'message':s})

def get_weather(reminders):
    umbrella = False
    city_id = 524901
    res = requests.get("http://api.openweathermap.org/data/2.5/forecast", params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': WeatherAppId})
    data = res.json()
    weather = 'Погода: '
    for i in data['list']:
        dt = str(int(i['dt_txt'].split()[1].strip('0').split(':')[0]) + 3)
        weather += '\n' + 'В ' + dt + ' будет ' + '{0:+3.0f}'.format(i['main']['temp']) + ' и ' + i['weather'][0]['description']
        if 'дождь' in i['weather'][0]['description']:
            umbrella = True
        if dt == '24':
            if umbrella:
                reminders[str(item['user_id'])].append('Не забудь взять зонтик!')
            return weather, reminders

def get_reminders():
    with open("data.json", "r") as f:
        s = f.read()
    r = json.loads(s)
    return r

reminders=get_reminders()

while True:
    response = vk.method('messages.get', values)
    if response['items']:
        values['last_message_id'] = response['items'][0]['id']
    for item in response['items']:
        if str.lower(item["body"])=='напоминание':
            write_msg(item['user_id'],'А какой текст?')
            response = vk.method('messages.get', values)
            while not response['items']:
                response = vk.method('messages.get', values)
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
        elif str.lower(item['body']) == 'мои напоминалочки':
            for reminder in reminders[str(item['user_id'])]:
                write_msg(item['user_id'], reminder)
        else:
            weather, reminders = get_weather(reminders)
            write_msg(item['user_id'],'Zdes budet mem')
            write_msg(item['user_id'], weather)
            for reminder in reminders:
                write_msg(item['user_id'], reminder)
        time.sleep(1)
        print(reminders)

