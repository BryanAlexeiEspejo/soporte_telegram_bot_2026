import os
import logging
from typing import Dict, List, Optional, Any

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("❌ TELEGRAM_BOT_TOKEN no configurado")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def safe_html(text: Optional[str]) -> str:
    if not text:
        return " "
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


class TelegramService:
    def __init__(self):
        self.api_url = TELEGRAM_API_URL

    # =========================
    # WEBHOOK
    # =========================
    async def set_webhook(self, webhook_url: str) -> bool:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{self.api_url}/setWebhook",
                json={"url": webhook_url}
            )
            data = resp.json()
            logger.info(f"setWebhook → {data}")
            return data.get("ok", False)

    async def delete_webhook(self) -> bool:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(f"{self.api_url}/deleteWebhook")
            return resp.json().get("ok", False)

    # =========================
    # MENSAJES
    # =========================
    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: Optional[str] = "HTML",
        reply_markup: Optional[Dict] = None,
        disable_web_page_preview: bool = True
    ) -> Dict[str, Any]:

        payload = {
            "chat_id": int(chat_id),
            "text": safe_html(text),
            "disable_web_page_preview": disable_web_page_preview
        }

        if parse_mode:
            payload["parse_mode"] = parse_mode
        if reply_markup:
            payload["reply_markup"] = reply_markup

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self.api_url}/sendMessage",
                json=payload
            )
            data = resp.json()
            if not data.get("ok"):
                logger.error(f"❌ send_message error: {data}")
            return data

    async def send_photo(
        self,
        chat_id: int,
        photo_url: str,
        caption: str = "",
        parse_mode: Optional[str] = "HTML"
    ) -> Dict[str, Any]:

        payload = {
            "chat_id": int(chat_id),
            "photo": photo_url,
            "caption": safe_html(caption)
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self.api_url}/sendPhoto",
                json=payload
            )
            return resp.json()

    async def send_document(
        self,
        chat_id: int,
        document_url: str,
        caption: str = "",
        parse_mode: Optional[str] = "HTML"
    ) -> Dict[str, Any]:

        payload = {
            "chat_id": int(chat_id),
            "document": document_url,
            "caption": safe_html(caption)
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self.api_url}/sendDocument",
                json=payload
            )
            return resp.json()

    async def send_location(
        self,
        chat_id: int,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:

        payload = {
            "chat_id": int(chat_id),
            "latitude": latitude,
            "longitude": longitude
        }

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{self.api_url}/sendLocation",
                json=payload
            )
            return resp.json()

    async def edit_message_text(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        parse_mode: Optional[str] = "HTML",
        reply_markup: Optional[Dict] = None
    ) -> Dict[str, Any]:

        payload = {
            "chat_id": int(chat_id),
            "message_id": int(message_id),
            "text": safe_html(text)
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if reply_markup:
            payload["reply_markup"] = reply_markup

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{self.api_url}/editMessageText",
                json=payload
            )
            return resp.json()

    async def delete_message(self, chat_id: int, message_id: int) -> bool:
        payload = {
            "chat_id": int(chat_id),
            "message_id": int(message_id)
        }

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{self.api_url}/deleteMessage",
                json=payload
            )
            return resp.json().get("ok", False)

    async def answer_callback_query(
        self,
        callback_query_id: str,
        text: str = "",
        show_alert: bool = False
    ) -> bool:

        payload = {
            "callback_query_id": callback_query_id,
            "text": safe_html(text),
            "show_alert": show_alert
        }

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{self.api_url}/answerCallbackQuery",
                json=payload
            )
            return resp.json().get("ok", False)

    # =========================
    # KEYBOARDS
    # =========================
    def create_inline_keyboard(self, buttons: List[List[Dict]]) -> Dict:
        return {"inline_keyboard": buttons}

    def create_reply_keyboard(self, buttons: List[List[str]], resize: bool = True) -> Dict:
        return {
            "keyboard": [[{"text": btn} for btn in row] for row in buttons],
            "resize_keyboard": resize,
            "one_time_keyboard": False
        }

    def remove_keyboard(self) -> Dict:
        return {"remove_keyboard": False}


telegram_service = TelegramService()
