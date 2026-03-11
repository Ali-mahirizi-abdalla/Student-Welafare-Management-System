import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def send_telegram_message(message, bot_token=None, chat_id=None):
    """
    Sends a message to a Telegram chat/channel using the Telegram Bot API.
    """
    token = bot_token or getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    chat = chat_id or getattr(settings, 'TELEGRAM_CHAT_ID', None)
    
    if not token or not chat:
        logger.error("Telegram token or chat_id not configured.")
        return False, "Telegram settings missing."

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat,
        'text': message,
        'parse_mode': 'Markdown'
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        result = response.json()
        if response.status_code == 200 and result.get('ok'):
            return True, "Broadcast sent successfully!"
        else:
            error_msg = result.get('description', 'Unknown error')
            logger.error(f"Telegram API Error: {error_msg}")
            return False, error_msg
    except Exception as e:
        logger.error(f"Telegram Connection Error: {str(e)}")
        return False, str(e)
