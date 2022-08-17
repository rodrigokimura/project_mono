"""Module to group Telegram related code"""
import requests
from django.conf import settings


def send_message(chat_id, text):
    """
    Send simple message via telegram
    """
    token = settings.TELEGRAM_BOT_TOKEN
    if token is None:
        return
    url = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}'
    requests.post(url)
