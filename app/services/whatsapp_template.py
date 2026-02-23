from typing import Dict, List


async def mensaje_no_entendido(nombre: str, numero: str) -> dict:
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": f"*¡Hola!* {nombre} 👋 *Soy AMI*, tu agente municipal inteligente del Gobierno Autónomo Municipal.\n"
                "Creo que no te entendí bien 🤔, vamos a intentarlo una vez más.\n"
                "Escríbeme algunas palabras clave sobre lo que estás buscando, por ejemplo:"
            },
            "footer": {
                "text": ". Contraseña iGOB\n. Pagos parqueos\n. Seguimiento trámites"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {"id": "catastro", "title": "Ver más Servicios"},
                    }
                ]
            },
        },
    }


# Creador de payload para sticker
async def mensaje_stiker(numero: str,id: str) -> dict:
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "sticker",
        "sticker": {"id": id },#699425366419244
    }


# Creador de payload para texto simple
async def crear_payload_texto(numero: str, cuerpo: str) -> dict:
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {"preview_url": False, "body": cuerpo},
    }


# Creador de payload con redirecionamiento
async def crear_payload_texto_url(
    numero: str, cuerpo: str, url: str, desc_url: str
) -> dict:
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "cta_url",
            # "header": {"type": "text", "text": option["header"]},
            "body": {"text": "*" + cuerpo + "*"},
            # "footer": {"text": option["footer"]},
            "action": {
                "name": "cta_url",
                "parameters": {
                    "display_text": desc_url,
                    "url": url,
                },
            },
        },
    }


async def crear_payload_lista(
    numero: str,
    cuerpo: str,
    opciones: list,
    header_text: str,
    footer_text: str,
    button_text: str,
) -> dict:
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": header_text,
            },
            "body": {"text": cuerpo},
            "footer": {"text": footer_text},
            "action": {
                "button": button_text,
                "sections": opciones,
            },
        },
    }


# Creador de payload para texto simple
async def crear_payload_button(
    numero: str, body: str, footer: str, id: str, texto_id: str
) -> dict:
    campo = ""
    if(footer != ""):
        campo = {"text": footer}
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            # "header": {"type": "image", "image": {"id": "2762702990552401"}},
            "body": {"text": body},
            "footer": campo,
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {"id": id, "title": texto_id},
                    }
                ]
            },
        },
    }

async def crear_payload_button_aux(
    numero: str, body: str, footer: str, id: str, texto_id: str
) -> dict:
    campo = ""
    if(footer != ""):
        campo = {"text": footer}
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            # "header": {"type": "image", "image": {"id": "2762702990552401"}},
            "body": {"text": body},
            "footer": campo,
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {"id": id, "title": texto_id},
                    },
                    {
                        "type": "reply",
                        "reply": {"id": "hola", "title": "Volver al inicio"},
                    },
                ]
            },
        },
    }