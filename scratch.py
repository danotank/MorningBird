import time
import vk_api
import json
vk = vk_api.VkApi(token = '7d07fa9396f2a078727fa4faf6b505e6998fdc5a5e2a9f94c064e58674fd36c53da1c473c2affa4b8822b')
values = {'out': 0,'count': 100,'time_offset': 60}
def write_msg(user_id, s):
    vk.method('messages.send', {'user_id':user_id,'message':s})


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
            write_msg(item['user_id'],'Привет!')
        time.sleep(1)
        print(reminders)

