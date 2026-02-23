import re

# ✅ UTILIDADES COMUNES

#text
def crear_payload_texto(numero: str, cuerpo: str, preview_url: bool = False) -> dict:
    """ Crea un payload de mensaje de texto para WhatsApp.
    Args:
        numero (str): Número de destino en formato internacional.
        mensaje (str): Texto del mensaje.
        preview_url (bool, optional): Si se debe mostrar preview de enlaces. Default: False."""
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {
            "preview_url": preview_url, # Si es True, muestra previsualización de enlaces (si hay enlaces)
            "body": cuerpo
        }
    }

#image (media_id generado en get_id_media(ruta_archivo: str, tipo: str))
def crear_payload_imagen(numero: str, media_id: str, caption: str = None) -> dict:
    """Crea un payload para enviar una imagen por WhatsApp.
    Args:
        numero (str): Número destino en formato internacional.
        media_id (str): ID de la imagen subida a WhatsApp.
        caption (str, optional): Texto de la imagen. Default: None."""
    image_payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "image",
        "image": { "id": media_id }
    }
    if caption:
        image_payload["image"]["caption"] = caption
    return image_payload

#documento (media_id generado en get_id_media(ruta_archivo: str, tipo: str))
def crear_payload_documento(numero: str, media_id: str, caption: str = None, filename: str = None) -> dict:
    """Crea un payload para enviar un documento por WhatsApp.
    Args:
        numero (str): Número destino en formato internacional.
        media_id (str): ID del documento subido a WhatsApp.
        caption (str, optional): Texto descriptivo del documento.
        filename (str, optional): Nombre del archivo a mostrar."""
    doc_payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "document",
        "document": { "id": media_id }
    }
    if caption:
        doc_payload["document"]["caption"] = caption
    if filename:
        doc_payload["document"]["filename"] = filename
    return doc_payload

#audio (media_id generado en get_id_media(ruta_archivo: str, tipo: str))
def crear_payload_audio(numero: str, media_id: str) -> dict:
    """Crea un payload para enviar un audio por WhatsApp.
    Args: numero (str): Número destino en formato internacional.
          media_id (str): ID del audio subido a WhatsApp."""
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "audio",
        "audio": { "id": media_id }
    }

#video (media_id generado en get_id_media(ruta_archivo: str, tipo: str))
def crear_payload_video(numero: str, media_id: str, caption: str = None) -> dict:
    """Crea un payload para enviar un video por WhatsApp.
    Args:   numero (str): Número destino en formato internacional.
            media_id (str): ID del video subido a WhatsApp.
            caption (str, optional): Texto descriptivo del video."""
    video_payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "video",
        "video": { "id": media_id }
    }
    if caption:
        video_payload["video"]["caption"] = caption
    return video_payload

#sticker (media_id generado en get_id_media(ruta_archivo: str, tipo: str))
def crear_payload_sticker(numero: str, media_id: str) -> dict:
    """Crea un payload para enviar un sticker por WhatsApp.
    Args:   numero (str): Número destino en formato internacional.
            media_id (str): ID del sticker subido a WhatsApp."""
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "sticker",
        "sticker": { "id": media_id }
    }

#ubicacion
def crear_payload_ubicacion( numero: str, lat: float, lon: float, name: str = None, address: str = None) -> dict:
    """Crea un payload para enviar una ubicación por WhatsApp.
    Args: numero (str): Número destino en formato internacional.
          latitude (float): Latitud de la ubicación.
          longitude (float): Longitud de la ubicación.
          name (str, optional): Nombre del lugar.
          address (str, optional): Dirección del lugar."""
    location = {    "latitude": lat,
                    "longitude": lon  }
    if name:
        location["name"] = name
    if address:
        location["address"] = address

    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "location",
        "location": location
    }

#contacto
def crear_payload_contacto( numero: str, formatted_name: str, nombre: str, apellido: str = "", fonos: list = None, emails: list = None) -> dict:
    """Crea un payload para enviar un contacto por WhatsApp.
    Args: numero (str): Número destino en formato internacional.
          formatted_name (str): Nombre completo del contacto.
          first_name (str): Primer nombre.
          last_name (str, optional): Apellido.
          phones (list, optional): Lista de teléfonos, cada uno como dict {"phone": "...", "type": "..."}.
          emails (list, optional): Lista de emails, cada uno como dict {"email": "..."}."""
    contact = {
        "name": { "formatted_name": formatted_name,
                  "first_name": nombre,
                  "last_name": apellido  }
    }
    if fonos:
        contact["phones"] = fonos
    if emails:
        contact["emails"] = emails

    return { "messaging_product": "whatsapp",
             "recipient_type": "individual",
             "to": numero,
             "type": "contacts",
             "contacts": [contact]}

#interactive -> button
def payload_interactivo_boton(numero: str, body: str, buttons: list, header: str = None, footer: str = None) -> dict:
    """Crea un payload para un mensaje interactivo de botones en WhatsApp.
    Args:
        numero (str): Número destino en formato internacional.
        header (str): Texto del encabezado.
        body (str): Texto principal del mensaje.
        footer (str): Texto del pie de mensaje.
        buttons (list): Lista de botones, cada uno como dict: [{"id": ..., "title": ...}, {"id": ..., "title": ...}]"""
    interactive = {
        "type": "button",
        "body": {"text": body},
        "action": { "buttons": buttons }
    }
    if header:
        interactive["header"] = {"type": "text", "text": header}
    if footer:
        interactive["footer"] = {"text": footer}

    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive": interactive
    }

#interactive -> list
def payload_interactivo_lista(numero: str, mensaje: str, secciones: list, btn_lbl: str) -> dict:
    """Crea un payload para un mensaje interactivo de lista en WhatsApp."""
    #secciones = [{ "title": "Trámites",
    #               "rows": [   {"id": "tramite1", "title": "Licencia", "description": "Solicita tu licencia"},
    #                           {"id": "tramite2", "title": "Permiso", "description": "Solicita tu permiso"} ]
    #               },
    #             { "title": "Consultas",
    #               "rows": [   {"id": "consulta1", "title": "Estado de trámite", "description": "Consulta el estado"},
    #                           {"id": "consulta2", "title": "Información general", "description": "Solicita información"} ]
    #               }]
    payload_interactive_list = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "list",
            #"header": {"type": "text", "text": "Servicios disponibles"},
            "body": {"text": mensaje},
            #"footer": {"text": "Puedes elegir solo uno"},
            "action": {
                "button": btn_lbl,
                "sections": secciones,
            }
        }
    }
    return payload_interactive_list

def crear_payload_texto_url(numero: str, cuerpo: str, url: str, desc_url: str) -> dict:
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "cta_url",
            "body": { "text": cuerpo },
            "action": {
                "name": "cta_url",
                "parameters": {"display_text": desc_url, "url": url},
            },
        },
    }

def crear_payload_exitbtn(numero: str, texto: str, id: str, titulo: str) -> dict:
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": f"{texto}"},
            "action": {
                "buttons": [{"type": "reply", "reply": {"id": id, "title": titulo}}]
            },
        },
    }

def payload_pin(numero: str, pin: str, fono_soporte: str) -> dict:
    numero = "59167134748"  # Reemplaza con el número destino
    pin = "123456"  # Reemplaza con el PIN real
    fono_soporte = "155"  # Reemplaza con el número de
    return  {
    "messaging_product": "whatsapp",
    "to": numero,  # Número destino en formato internacional, ej: "591XXXXXXXXX"
    "type": "template",
    "template": {
        "name": "chk_igob",  # El nombre exacto de tu plantilla
        "language": { "code": "es_MX" },  # El idioma que elegiste
        "components": [
            {
                "type": "body",
                "parameters": [
                    { "type": "text", "text": pin },         # Valor para {{1}}
                    { "type": "text", "text": fono_soporte } # Valor para {{2}}
                ]
            }
        ]
    }
}

#Validadores comunes
def mail_valido(texto: str) -> bool:
    patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(patron, texto) is not None

def ci_valido(texto: str) -> bool:
    patron = r"^\d+(-[a-z]+)?$"
    return re.fullmatch(patron, texto) is not None and len(texto) >= 5

def ofuscar_correo(correo: str) -> str:
    if '@' not in correo:
        return correo
    usuario, dominio = correo.split('@', 1)
    if len(usuario) <= 4:
        usuario_oculto = usuario
    else:
        usuario_oculto = usuario[:2] + '*' * (len(usuario) - 4) + usuario[-2:]
    return usuario_oculto + '@' + dominio