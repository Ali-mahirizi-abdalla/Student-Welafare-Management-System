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
        return False, "Telegram settings missing in .env"

    # Minimal escaping for Markdown V1 body
    # Only escape characters in the 'message' part, not the alert level header 
    # which we control in the view.
    
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
            # Handle Markdown parsing errors specifically for better feedback
            if "can't parse" in error_msg.lower():
                error_msg += ". Try removing special characters like _ or * from your message."
            
            logger.error(f"Telegram API Error: {error_msg}")
            return False, error_msg
    except Exception as e:
        logger.error(f"Telegram Connection Error: {str(e)}")
        return False, f"Connection failed: {str(e)}"
