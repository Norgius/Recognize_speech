from environs import Env
from random import randint

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType

from connect_dialogflow import detect_intent_texts

RUS_LANGUAGE_CODE = 'ru-RU'


def reply_to_message(event, vk_api, project_id, session_id):
    answer = detect_intent_texts(
        project_id, session_id, event.text, RUS_LANGUAGE_CODE
    )
    vk_api.messages.send(
        user_id=event.user_id,
        message=answer,
        random_id=randint(1, 100000)
    )


def main():
    env = Env()
    env.read_env()
    vk_token = env.str('VK_GROUP_TOKEN')
    project_id = env.str('PROJECT_ID')
    session_id = env.str('TELEGRAM_ID')

    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            reply_to_message(event, vk_api, project_id, session_id)


if __name__ == '__main__':
    main()
