from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse, HTMLResponse

from app.controllers.telegram_controller import (
    handle_telegram_webhook,
    setup_telegram_webhook
)
from app.services.telegram_service import telegram_service

router = APIRouter()

@router.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    """Endpoint para el webhook de Telegram"""
    return await handle_telegram_webhook(request)

@router.get("/telegram/webhook")
async def verify_webhook(request: Request):
    """Verificar que el webhook está activo"""
    return JSONResponse(content={"status": "active", "platform": "telegram"})

@router.post("/telegram/setup-webhook")
async def setup_webhook():
    """Configurar el webhook de Telegram (usar una vez)"""
    success = await setup_telegram_webhook()
    return JSONResponse(content={
        "success": success,
        "message": "Webhook configurado" if success else "Error configurando webhook"
    })

@router.post("/telegram/send-message")
async def send_telegram_message(
    chat_id: int,
    message: str,
    parse_mode: str = "HTML"
):
    """Enviar mensaje manual a Telegram"""
    try:
        result = await telegram_service.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode=parse_mode
        )
        return JSONResponse(content={
            "success": True,
            "message_id": result.get("result", {}).get("message_id")
        })
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "error": str(e)
        }, status_code=500)

@router.get("/telegram/get-updates")
async def get_updates(offset: int = None, limit: int = 10):
    """Obtener updates de Telegram (para testing)"""
    url = f"https://api.telegram.org/bot{telegram_service.bot_token}/getUpdates"
    
    params = {"limit": limit}
    if offset:
        params["offset"] = offset
    
    import requests
    response = requests.get(url, params=params)
    return JSONResponse(content=response.json())

@router.get("/telegram/bot-info")
async def get_bot_info():
    """Obtener información del bot"""
    try:
        user_info = await telegram_service.get_user_info("me")  # "me" es el bot
        return JSONResponse(content=user_info)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)