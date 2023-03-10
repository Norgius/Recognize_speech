import logging
from time import sleep
from functools import partial

from environs import Env
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext import Filters, CallbackContext
from telegram.error import NetworkError, TelegramError
from utils import TelegramLogsHandler, detect_intent_texts

RUS_LANGUAGE_CODE = 'ru-RU'

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        'Здравствуйте, надеемся, что данный бот вам поможет'
    )


def reply_to_message(update: Update, context: CallbackContext,
                     project_id) -> None:
    session_id = f'tg-{update.effective_user.id}'

    try:
        answer = detect_intent_texts(
            project_id, session_id, update.message.text, RUS_LANGUAGE_CODE
        )
        update.message.reply_text(answer.fulfillment_text)
    except NetworkError as netword_error:
        logger.warning(f'Ошибка сети телеграм бота\n{netword_error}\n')
        sleep(20)
    except TelegramError as telegram_error:
        logger.warning(f'Ошибка телеграм бота\n{telegram_error}\n')


def main() -> None:
    env = Env()
    env.read_env()
    speech_bot_token = env.str('SPEECH_BOT_TELEGRAM_TOKEN')
    person_id = env.str('PERSON_ID')
    project_id = env.str('PROJECT_ID')
    error_log_bot_token = env.str('ERROR_LOG_BOT_TOKEN')

    error_log_bot = Bot(error_log_bot_token)
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(error_log_bot, person_id))

    speech_bot = Updater(speech_bot_token)
    dispatcher = speech_bot.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(
        MessageHandler(
            Filters.text & ~Filters.command,
            partial(reply_to_message, project_id=project_id)
        )
    )
    logger.info('Запуск телеграм бота')
    while True:
        speech_bot.start_polling()
        speech_bot.idle()


if __name__ == '__main__':
    main()
