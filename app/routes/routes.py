from fastapi import APIRouter, HTTPException
from app.models.message_model import PlacaUpdateRequest,notificationRequest
from app.database.database import db
from bson import ObjectId
#from app.services.whatsapp_service import enviar_mensaje_whatsapp
from app.services.msg_handler import MessageHandler
from datetime import datetime, timedelta
from typing import Any

router = APIRouter()
handler = MessageHandler()

@router.get("/list")
async def get_reservas():
    inicio_dia = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    fin_dia = inicio_dia + timedelta(days=1)

    cursor = db.reservas.find({
        "placa":"abc-123484",
        "fechaRegistro": {
            "$gte": inicio_dia,
            "$lt": fin_dia
        }
    })
    resultados = await cursor.to_list(length=1)
    for doc in resultados:
        doc["_id"] = str(doc["_id"])

    return resultados



def calcular_hora(hora_inicio,hora_fin):
    formato = "%H:%M"
    inicio = datetime.strptime(hora_inicio, formato)
    fin = datetime.strptime(hora_fin, formato)

    # Calcular la diferencia
    diferencia = fin - inicio

    # Mostrar la diferencia en horas y minutos
    horas = diferencia.seconds // 3600
    minutos = (diferencia.seconds % 3600) // 60
    return f"{horas} horas y {minutos} minutos"

@router.put("/modify_plate")
async def modificar_placa(request: PlacaUpdateRequest):
    print(request)

    inicio_dia = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    fin_dia = inicio_dia + timedelta(days=1)

    filtro = {
        "placa": request.placa.lower(),
        "fechaRegistro": {
            "$gte": inicio_dia,
            "$lt": fin_dia
        }
    }

    nuevo_valor = {"$set": {"estado": "REGISTRADO"}}

    resultado = await db.reservas.update_one(filtro, nuevo_valor)

    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="No se encontró una reserva con esa placa en el día actual.")

    if resultado.modified_count == 0:
        return {"mensaje": "No se realizaron cambios. El estado ya era REGISTRADO."}

    
    reserva = await db.reservas.find_one(filtro)
    if not reserva:
        raise HTTPException(status_code=500, detail="Error al obtener los datos de la reserva actualizada.")

    telefono_usuario = reserva.get("numero")  # COMO SACO ESTE NUMERO DE LA BASE DE DATOS
    tiempo_contratado = calcular_hora(reserva.get("horaInicio"),reserva.get("horaFin"))
    mensaje = (
        "#notificaciones#"
        "✅ *VERIFICACIÓN EXITOSA*\n"
        "Hemos confirmado tu pago de parqueo con los siguientes datos:\n"
        f"- N° de pago: 1234567\n"
        f"- Placa: {request.placa.upper()}\n"
        f"- Tiempo contratado: {tiempo_contratado} (hasta las {reserva.get('horaFin')})\n"
        f"- Ubicación: {reserva.get('parqueo')}\n\n"
        "📣 Recibirás una notificación 15 minutos antes de que finalice tu tiempo.\n"
        "¿Necesitas más tiempo? Puedes extender tu parqueo desde el mismo sistema."
    )
    try:
        await handler.process_message(mensaje, telefono_usuario,'')
    except Exception as e:
        return {
            "mensaje": "Estado actualizado, pero hubo un error al enviar el mensaje por WhatsApp.",
            "error": str(e)
        }

    return {
        "mensaje": "Estado actualizado y mensaje enviado por WhatsApp.",
        "modificados": resultado.modified_count,
        "placa": request.placa.upper(),
        "telefono": telefono_usuario
    }


@router.post("/send_notification")
async def notificar(request: notificationRequest) -> dict[str, Any]:
    print("request",request)
    try:
        await handler.process_message(request.mensaje, request.numero.upper(),'')
    except Exception as e:
        return {
            "mensaje": "Hubo un error al enviar el mensaje por WhatsApp.",
            "error": str(e)
        }

    return {
        "mensaje": "Mensaje enviado por WhatsApp."
    }

@router.post("/send_notification-text")
async def notificar(request: notificationRequest) -> dict[str, Any]:
    print("request",request)
    try:
        data = [{
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": f"591{request.numero}",
            "type": "text",
            "text": {
                "preview_url": True,
                "body": request.mensaje
            }
        }]
        await handler.send_messages(data)
    except Exception as e:
        return {
            "mensaje": "Hubo un error al enviar el mensaje por WhatsApp.",
            "error": str(e)
        }

    return {
        "mensaje": "Mensaje enviado por WhatsApp."
    }
