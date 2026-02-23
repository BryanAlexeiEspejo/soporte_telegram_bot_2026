import requests
import json
import re
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

# - URLS DE SERVICIOS EXTERNOS - ✅ ESTAS SE MANTIENEN ACTIVAS
URL_IGOB= os.getenv("IGOB_API")
URL_GMOT= os.getenv("GMOT_API")
ORI_GMOT= os.getenv("ORIGEN_GMOT")
URL_CBRA= os.getenv("CBRA_API")

# - URLS DE SERVICIOS WHATSAPP 
PAGE_ID = os.getenv("PAGE_ID", "943298252203190")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL", f"https://graph.facebook.com/v22.0/{PAGE_ID}/messages")
HEADERS = {"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"}




# - CONSUMO DE SERVICIOS EXTERNOS - ✅ ESTAS SE MANTIENEN ACTIVAS
async def obtener_profesiones(params: dict = None) -> dict:
    url = f"{URL_CBRA}/registro-ciudadano/profesion"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()  # <-- CORRECTO, sin await
    except httpx.RequestError as e:
        print(f"❌ Error al consumir servicio externo: {e}")
        return {"error": str(e)}

async def buscar_ciudadano(payload: dict) -> dict:
    url = f"{URL_CBRA}/registro-ciudadano/buscar-ciudadano-generico"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json() 
    except httpx.RequestError as e:
        print(f"❌ Error al consumir servicio externo: {e}")
        return {"error": str(e)}

async def recuperar_pin_ciudadano(payload: dict) -> dict:
    """ POST: recupera pin de iGOB enviando form-data """
    url = f"{URL_IGOB}/wsRCIgob/recuperarPINV2" #Externa pruebas
    form_data = {
            "usuario": payload.get("usuario", ""),
            "correo": payload.get("correo", "")
        }
    try:
        async with httpx.AsyncClient(timeout=20.0) as client: #El servicio esta inestable, tarda entre 3 a 20 segunsos en responder
            response = await client.post(url, data=form_data)
            response.raise_for_status()
            data = response.json()
            # Si existe la ruta al campo body y es un string JSON, lo convertimos a dict
            try:
                options = data.get("success", {}).get("options:", None)
                if options and "body" in options and isinstance(options["body"], str):
                    options["body"] = json.loads(options["body"])
            except Exception as e:
                print(f"❌ Error al convertir body a dict: {e}")
            return data
    except httpx.RequestError as e:
        print(f"❌ Error al consumir servicio externo para recuperar el PIN: {e}")
        return {"error": {"no_service":True}, "message": str(e)}
    
async def consulta_tramite(payload: dict) -> dict:
    #url = f"{URL_GMOT}/wsSTTF/eSitramNumCont"
    url = f'{URL_GMOT}/wsSTTF/eSitramNumCont'
    ##url = "http://serviciosrs.lapaz.bo/wsSTTF/eSitramNumCont"
    payload = {
        "numtramite": payload.get("numero", ""),
        "contrasenia": payload.get("contra", ""),
    }
    headers = {
        #"Origin":  "http://sitram247iconsulta.lapaz.bo",
        "Origin":  f'{ORI_GMOT}',
        "Content-Type": "application/json"
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            # Si existe la ruta al campo body y es un string JSON, lo convertimos a dict
            #try:
            options = data.get("success", {}).get("options:", None)
            if options and "body" in options and isinstance(options["body"], str):
                options["body"] = json.loads(options["body"])
            #except Exception as e:
                #print(f"❌ Error al convertir body a dict: {e}")
            print(data)
            return data
    except httpx.RequestError as e:
        print(f"❌ Error al consumir servicio externo para verificar el etado del tramite: {e}")
        return {"error": {"no_service":True}, "message": str(e)}
    
# - CONSUMO DE SERVICIOS WHATSAPP PARA UTILITARIOS
def get_id_media(ruta_archivo: str, tipo: str) -> str:
    """Sube un archivo (imagen, documento, audio, video) al servidor de WhatsApp y devuelve el media_id.
    Args: ruta_archivo (str): Ruta local del archivo a subir.
          tipo (str): Tipo de archivo ('image', 'document', 'audio', 'video')."""
    # Mapear tipo a MIME
    mime_map = {
        "image": "image/jpeg",
        "document": "application/pdf",
        "audio": "audio/mpeg",
        "video": "video/mp4"
    }
    mime_type = mime_map.get(tipo, "application/octet-stream")

    headers = { "Authorization": f"Bearer {ACCESS_TOKEN}" }
    files = { "file": open(ruta_archivo, "rb") }
    data = {  "messaging_product": "whatsapp", "type": mime_type }
    # El endpoint para subir media es diferente al de mensajes
    try:
        response = requests.post(WHATSAPP_API_URL, headers=headers, files=files, data=data)
        response.raise_for_status()
        media_id = response.json().get("id")
        return media_id
    except Exception as e:
        print(f"❌ Error al subir {tipo} a WhatsApp: {e}")
        return None
    finally:
        files["file"].close()

async def recuperarContraseniaCel(payload: dict) -> dict:
    #url = f'{URL_GMOT}/wsSTTF/eSitramNumCont'
    url = 'http://131.0.0.17:9089/wsRCIgob/recuperarContraseniaCel'
    payload = {
        "usuario": payload.get("usuario"),
        "celular": payload.get("celular"),
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            options = data.get("success", {}).get("options:", None)
            if options and "body" in options and isinstance(options["body"], str):
                options["body"] = json.loads(options["body"])
            print(data)
            return data
    except httpx.RequestError as e:
        print(f"❌ Error al consumir servicio: {e}")
        return {"error": {"no_service":True}, "message": str(e)}