import pika
import json
import asyncio
import os
import time
from dotenv import load_dotenv
from app.services.msg_handler import MessageHandler  # ✅ CAMBIO
from app.database.database import  buscar_mensaje_procesado,  registrar_mensaje_procesado 

load_dotenv()
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672")

def safe_get(dic, path, default=None):
    for key in path:
        try:
            dic = dic[key]
        except (KeyError, IndexError, TypeError):
            return default
    return dic

async def procesar_mensaje_async(msg, name):
    numero = msg.get("from")
    tipo = msg.get("type")
    mensaje_id = msg.get("id")
    consumer_id = os.getpid()

    try:
        if await buscar_mensaje_procesado(mensaje_id):
            print(f"Mensaje {mensaje_id} ya procesado, ignorando.")
            return

        handler = MessageHandler()
        #print(f"Procesando mensaje {mensaje_id} de {name} ({numero}) tipo: {tipo}")
        #inicio = time.time()
        if tipo == "interactive":
            inter = msg.get("interactive", {})
            if inter.get("type") == "button_reply":
                text = inter["button_reply"]["id"]
                responses = await handler.process_message(text, numero, name, mensaje_id, consumer_id)
                await handler.send_messages(responses)
                #print("-Ejecucion:->", time.time() - inicio)
            elif inter.get("type") == "list_reply":
                text = inter["list_reply"]["id"]
                responses = await handler.process_message(text, numero, name, mensaje_id, consumer_id)
                await handler.send_messages(responses)
                #print("-Ejecucion:->", time.time() - inicio)
        elif tipo == "text":
            text = msg["text"]["body"]
            responses = await handler.process_message(text, numero, name, mensaje_id, consumer_id)
            await handler.send_messages(responses)
            #print("-Ejecucion:->", time.time() - inicio)
    except Exception as e:
        print(f"❌ Error procesando mensaje {mensaje_id}: {e}")
    finally:
        # Registrar el mensaje como procesado SIEMPRE, incluso si hubo error
        await registrar_mensaje_procesado(mensaje_id)

def procesar_mensaje(body, loop):
    mensajes = body.get("entry", [])[0].get("changes", [])[0].get("value", {}).get("messages", [])
    name = safe_get(body, ["entry", 0, "changes", 0, "value", "contacts", 0, "profile", "name"], "Desconocido")

    if mensajes:
        msg = mensajes[0]
        loop.run_until_complete(procesar_mensaje_async(msg, name))

def main():  #corre como proceso independiente pero se inicia como hilo con el fastapi
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    #channel.queue_declare(queue='whatsapp_in', durable=True)  # Sin TTL
    channel.queue_declare(queue='whatsapp_in', durable=True, arguments={'x-message-ttl': 1800000}) # Mensajes expiran en 30 minutos si no son consumidos
    channel.basic_qos(prefetch_count=1)  # <-- Control de concurrencia

    # Crea un bucle persistente para este hilo q mantien multpes converciones y no se cerrara hasta que el hilo termine
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def callback(ch, method, properties, body):
        try:
            mensaje = json.loads(body)
            procesado_ok = False
            try:
                procesar_mensaje(mensaje, loop)  # Esto ejecuta el async y espera
                procesado_ok = True
            except Exception as e:
                print(f"❌ Error procesando mensaje en procesar_mensaje: {e}")
                # Si quieres, puedes loggear el error aquí

            if procesado_ok:
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                # Si el mensaje ya fue procesado, no lo reencoles
                # Si el error es recuperable, puedes reencolar
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            print(f"❌ Error general en callback: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    channel.basic_consume(queue='whatsapp_in', on_message_callback=callback)
    print('Esperando mensajes de Telegram. Presiona CTRL+C para salir.')
    channel.start_consuming()

if __name__ == "__main__":
    main()