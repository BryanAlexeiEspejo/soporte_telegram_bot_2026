import pika
import json
import os
from dotenv import load_dotenv
import pika
import json
import os
import re
from dotenv import load_dotenv
from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse
from app.services.whatsapp_service import obtener_profesiones, buscar_ciudadano, recuperar_pin_ciudadano
from app.database.database import set_estado_usuario, get_estado_usuario, get_hora_mongo
from datetime import datetime
load_dotenv()

TOKEN_GAMLP = os.getenv("TOKEN_GAMLP", "BOTAMI")  # Token de verificación del webhook
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

def publicar_en_cola_rabbitmq(mensaje: dict):
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue='whatsapp_in', durable=True, arguments={'x-message-ttl': 1800000})
    channel.basic_publish(
        exchange='',
        routing_key='whatsapp_in',
        body=json.dumps(mensaje),
        properties=pika.BasicProperties( delivery_mode=2 ) # hace el mensaje persistente en rabbitMQ
    )
    connection.close()

async def handle_get_webhook(request: Request):
    params = dict(request.query_params)
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    if token == TOKEN_GAMLP and challenge:
        return HTMLResponse(content=challenge)
    return JSONResponse(status_code=401, content={"error": "Token Inválido"})

def safe_get(d: dict, keys: list, default=None):
    """Accede de forma segura a claves anidadas."""
    for key in keys:
        if isinstance(d, list):
            if not d or not isinstance(key, int) or key >= len(d):
                return default
            d = d[key]
        elif isinstance(d, dict):
            d = d.get(key, default)
        else:
            return default
    return d
    
async def handle_post_webhook(request: Request):
    #Nota se encola el mensaje solo si no hay diferencia meno a 1.5 segundos entre la hora del estado y la hora del mongo
    try:
        body = await request.json()
        numero = safe_get(body, ["entry", 0, "changes", 0, "value", "messages", 0, "from"])
        msg = safe_get(body, ["entry", 0, "changes", 0, "value", "messages", 0], {})
        msg_type = msg.get("type")

        if msg_type == "text":
            texto = safe_get(msg, ["text", "body"])
        elif msg_type == "interactive":
            interactive_type = safe_get(msg, ["interactive", "type"])
            if interactive_type == "list_reply":
                texto = safe_get(msg, ["interactive", "list_reply", "id"])
            elif interactive_type == "button_reply":
                texto = safe_get(msg, ["interactive", "button_reply", "id"])
            else:
                texto = None
        else:
            texto = None
        #texto = safe_get(body, ["entry", 0, "changes", 0, "value", "messages", 0, "text", "body"])
        estado = await get_estado_usuario(numero)
        await set_estado_usuario(numero, {})
        hora_mongo = await get_hora_mongo()

        if not es_texto_valido(texto):
            return JSONResponse(content={"message": "INVALID_TEXT"})
        if estado:
            if numero:
                hora_estado = estado.get("updated_at")
                if hora_estado is not None:
                    if isinstance(hora_estado, str):
                        hora_estado = datetime.fromisoformat(hora_estado)
                    diferencia = abs((hora_mongo - hora_estado).total_seconds())
                    if diferencia < 0.75:
                        return JSONResponse(content={"message": "EVENT_RECEIVED_PREVIOUSLY"})
                    elif diferencia >= 1800:
                        """ Si la diferencia es mayor a 30 minutos, se asume que el estado es obsoleto y se limpia."""
                        await set_estado_usuario(numero, {"contexto": "", "estado": "", "ci": "", "mail": ""})
                    #print(f"Diferencia {diferencia}")
                    
            else:
                return JSONResponse(content={"message": "NO_NUMBER_IN_MESSAGE"})
        publicar_en_cola_rabbitmq(body)
        return JSONResponse(content={"message": "EVENT_RECEIVED"})
    except Exception as e:
        print("Error:", e)
        return JSONResponse(content={"message": "ERROR_PROCESSING"}, status_code=500)
    
async def handle_get_professions(request: Request):
    """ Maneja la solicitud GET para obtener profesiones."""
    try:
        params = dict(request.query_params)
        data = await obtener_profesiones(params)
        return JSONResponse(content=data)
    except Exception as e:
        print("Error:", e)
        return JSONResponse(content={"message": "ERROR_PROCESANDO"}, status_code=500)   

async def handle_post_ciudadano(request: Request):
    """ Maneja la solicitud POST para buscar ciudadano."""
    try:
        payload = await request.json()
        data = await buscar_ciudadano(payload)
        return JSONResponse(content=data)
    except Exception as e:
        print("Error:", e)
        return JSONResponse(content={"message": "ERROR_PROCESANDO"}, status_code=500)

async def handle_post_recuperar_pin_ciudadano(request: Request):
    """ Maneja la solicitud POST para recuperar el pin ciudadano."""
    try:
        payload = await request.json()
        data = await recuperar_pin_ciudadano(payload)
        return JSONResponse(content=data)
    except Exception as e:
        print("Error:", e)
        return JSONResponse(content={"message": "ERROR_PROCESANDO_PIN"}, status_code=500)

def es_texto_valido(texto: str) -> bool:
    """
    Verifica si el texto es válido:
    - Retorna False si solo es un caracter.
    - Retorna False si todos los caracteres son signos o símbolos.
    - Retorna True si contiene al menos una letra o número y tiene más de un caracter.
    """
    if not texto or len(texto.strip()) <= 1:
        return False
    # Regex para detectar si el texto contiene solo signos/símbolos (no letras ni números)
    # ^[\W_]+$ -> solo símbolos, espacios y guiones bajos
    if re.fullmatch(r'[\W_]+', texto):
        return False
    return True

