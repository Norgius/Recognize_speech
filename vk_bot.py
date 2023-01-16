import logging
import uuid
from time import sleep
from random import randint

from environs import Env
from telegram import Bot
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from requests.exceptions import ReadTimeout, ConnectionError

from utils import TelegramLogsHandler, detect_intent_texts

RUS_LANGUAGE_CODE = 'ru-RU'

logger = logging.getLogger(__name__)


def reply_to_message(event, vk_api, project_id):
    session_id = f'vk-{event.user_id}'
    answer = detect_intent_texts(
        project_id, session_id, event.text, RUS_LANGUAGE_CODE)
    if not answer.intent.is_fallback:
        vk_api.messages.send(
            user_id=event.user_id,
            message=answer.fulfillment_text,
            random_id=randint(1, 100000)
        )


def main():
    env = Env()
    env.read_env()
    vk_token = env.str('VK_GROUP_TOKEN')
    project_id = env.str('PROJECT_ID')
    session_id = str(uuid.uuid4())
    person_id = env.str('PERSON_ID')
    error_log_bot_token = env.str('ERROR_LOG_BOT_TOKEN')

    error_log_bot = Bot(error_log_bot_token)
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(error_log_bot, person_id))

    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    logger.info('Запуск VK бота')

    while True:
        try:
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    reply_to_message(event, vk_api, project_id)
        except ReadTimeout as timeout:
            logger.warning(f'Превышено время ожидания VK бота\n{timeout}\n')
        except ConnectionError as connect_er:
            logger.warning(f'Произошёл сетевой сбой VK бота\n{connect_er}\n')
            sleep(20)


if __name__ == '__main__':
    main()
