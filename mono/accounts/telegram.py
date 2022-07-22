import requests
from django.conf import settings


def send_message(chat_id, text):
    TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={text}'
    requests.post(url)
