# app/utils/telegram_send.py
import os
import aiohttp
import logging

logger = logging.getLogger(__name__)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # configúralo

async def send_telegram_text(chat_id: str, text: str, parse_mode: str = "Markdown") -> bool:
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN no configurado")
        return False
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=10) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    logger.error("Telegram send error: status=%s body=%s", resp.status, body)
                    return False
                return True
    except Exception:
        logger.exception("Error enviando mensaje a Telegram")
        return False
