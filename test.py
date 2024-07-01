from telegram import Bot
from telegram.error import TelegramError
import time
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import subprocess


def send_test_message(message):
        chat_id = "-4248092135"
        bot = Bot(token="7337195716:AAHFpNJk6OrbRZU-2vcLfRarAKyXU2mXCaI")
        try:
            bot.send_message(chat_id=chat_id, text=message,
                             parse_mode='Markdown')
            time.sleep(5)
        except Exception as ex:
            print(ex)
message = "\U0001F525"
send_test_message(message)