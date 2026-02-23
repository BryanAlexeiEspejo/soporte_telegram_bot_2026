import os
import json
import logging
from typing import Dict, Any, List

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from app.services.msg_handler import MessageHandler
from app.database.database import get_or_create_telegram_user

from app.services.telegram_service import telegram_service

logger = logging.getLogger(__name__)
handler = MessageHandler()

async def handle_telegram_webhook(request: Request):
    """Maneja las actualizaciones del webhook de Telegram"""
    try:
        update = await request.json()
        logger.debug(f"Update recibido: {json.dumps(update, indent=2)}")

        # Procesar diferentes tipos de updates
        if "message" in update:
            return await handle_message(update["message"])
        elif "callback_query" in update:
            return await handle_callback_query(update["callback_query"])
        elif "edited_message" in update:
            return await handle_edited_message(update["edited_message"])
        else:
            logger.warning(f"Tipo de update no soportado: {list(update.keys())}")
            return JSONResponse(content={"status": "ok"})
    except Exception as e:
        logger.exception("Error procesando webhook")
        raise HTTPException(status_code=500, detail=str(e))


async def handle_message(message: Dict[str, Any]):
    """Procesa mensajes de texto y otros tipos (envía todo al MessageHandler)"""
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    message_id = message.get("message_id")

    # Obtener información del usuario
    user = message.get("from", {})
    user_id = user.get("id")
    username = user.get("username", "")
    first_name = user.get("first_name", "")
    last_name = user.get("last_name", "")

    # Crear nombre completo
    name_parts = []
    if first_name:
        name_parts.append(first_name)
    if last_name:
        name_parts.append(last_name)
    name = " ".join(name_parts) if name_parts else username or str(user_id)

    # Guardar/actualizar usuario en la base de datos (no bloquear si falla)
    try:
        await get_or_create_telegram_user(
            telegram_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            chat_id=chat_id
        )
    except Exception:
        logger.exception("Error guardando usuario de Telegram")

    # Normalizar payload a un "texto" que entiende msg_handler
    texto_input = None
    if "text" in message:
        texto_input = message.get("text")
    elif "contact" in message:
        # reenviamos como texto indicando contacto
        contact = message.get("contact", {})
        texto_input = f"[CONTACT]{contact.get('phone_number','')}"
    elif "location" in message:
        loc = message.get("location", {})
        texto_input = f"[LOCATION]{loc.get('latitude','')},{loc.get('longitude','')}"
    elif "photo" in message:
        texto_input = "[PHOTO]"
    elif "document" in message:
        doc = message.get("document", {})
        texto_input = f"[DOCUMENT]{doc.get('file_name','documento')}"

    # Si no hay nada manejable devolvemos OK
    if texto_input is None:
        return JSONResponse(content={"status": "ok"})

    # Enviar al handler central (msg_handler) indicando plataforma = telegram
    try:
        responses = await handler.process_message(
            texto=texto_input,
            numero=str(chat_id),
            name=name,
            msg_id=str(message_id or ""),
            platform="telegram"
        )

        # Adaptar respuestas retornadas por msg_handler al formato Telegram
        telegram_responses = await handler.adapt_responses_for_telegram(responses)

        # Enviar las respuestas adaptadas
        for resp in telegram_responses:
            try:
                await telegram_service.send_message(**resp)
            except Exception:
                logger.exception("Error enviando mensaje a Telegram")

    except Exception:
        logger.exception("Error procesando mensaje desde Telegram")
        # Notificar al usuario sobre el error
        try:
            await telegram_service.send_message(
                chat_id=chat_id,
                text="❌ Ocurrió un error procesando tu mensaje. Por favor, inténtalo de nuevo."
            )
        except Exception:
            logger.exception("Error enviando aviso de error a Telegram")

    return JSONResponse(content={"status": "ok"})


async def handle_callback_query(callback_query: Dict[str, Any]):
    """Procesa callbacks de botones inline delegando al msg_handler"""
    try:
        user = callback_query.get("from", {})
        callback_id = callback_query.get("id")
        data = callback_query.get("data", "") or ""
        message = callback_query.get("message", {}) or {}
        chat_id = message.get("chat", {}).get("id")
        message_id = message.get("message_id")

        username = user.get("username", "")
        first_name = user.get("first_name", "")
        last_name = user.get("last_name", "")
        name_parts = []
        if first_name:
            name_parts.append(first_name)
        if last_name:
            name_parts.append(last_name)
        name = " ".join(name_parts) if name_parts else username or str(user.get("id"))

        # Responder callback para quitar "loading" (no mostramos texto)
        try:
            await telegram_service.answer_callback_query(callback_query_id=callback_id, text="")
        except Exception:
            logger.exception("Error respondiendo callback_query (answer)")

        # Delegar el contenido (data) al handler como si fuera texto
        try:
            responses = await handler.process_message(
                texto=data,
                numero=str(chat_id),
                name=name,
                msg_id=str(message_id or ""),
                platform="telegram"
            )

            telegram_responses = await handler.adapt_responses_for_telegram(responses)
            for resp in telegram_responses:
                try:
                    await telegram_service.send_message(**resp)
                except Exception:
                    logger.exception("Error enviando respuesta de callback a Telegram")

        except Exception:
            logger.exception("Error procesando callback en msg_handler")
            try:
                await telegram_service.send_message(
                    chat_id=chat_id,
                    text="❌ Ocurrió un error procesando tu selección."
                )
            except Exception:
                logger.exception("Error enviando mensaje de fallo callback")

        return JSONResponse(content={"status": "ok"})

    except Exception:
        logger.exception("Error en handle_callback_query")
        return JSONResponse(content={"status": "error"}, status_code=500)


async def handle_edited_message(edited_message: Dict[str, Any]):
    """Procesa mensajes editados (delegamos también al handler si queremos)"""
    try:
        chat_id = edited_message.get("chat", {}).get("id")
        message_id = edited_message.get("message_id")
        texto_input = edited_message.get("text") or "[EDITED]"

        # Delegar edición al handler (opcional)
        try:
            responses = await handler.process_message(
                texto=texto_input,
                numero=str(chat_id),
                name=str(edited_message.get("from", {}).get("first_name", "")),
                msg_id=str(message_id or ""),
                platform="telegram"
            )
            telegram_responses = await handler.adapt_responses_for_telegram(responses)
            for resp in telegram_responses:
                try:
                    await telegram_service.send_message(**resp)
                except Exception:
                    logger.exception("Error enviando respuesta a mensaje editado")
        except Exception:
            logger.exception("Error delegando mensaje editado al handler")

        return JSONResponse(content={"status": "ok"})
    except Exception:
        logger.exception("Error en handle_edited_message")
        return JSONResponse(content={"status": "error"}, status_code=500)


async def setup_telegram_webhook():
    """Configura el webhook de Telegram (helper usado en startup)"""
    webhook_url = os.getenv("TELEGRAM_WEBHOOK_URL")
    if not webhook_url or webhook_url == "https://tudominio.com/telegram/webhook":
        print("⚠️ TELEGRAM_WEBHOOK_URL no configurado o usando valor por defecto")
        print("⚠️ Configura TELEGRAM_WEBHOOK_URL en .env con tu URL de ngrok")
        return False
    try:
        success = await telegram_service.set_webhook(webhook_url)
        if success:
            print("✅ Webhook de Telegram configurado exitosamente")
        else:
            print("❌ Error configurando webhook de Telegram")
        return success
    except Exception:
        logger.exception("Error configurando webhook")
        return False
