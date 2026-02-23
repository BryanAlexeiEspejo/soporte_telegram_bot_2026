import os
from typing import List, Dict, Any
from app.database.database import set_estado_usuario
from app.services.whatsapp_template import crear_payload_texto
from .base_handler import BaseHandler
from app.services.utils.utils_handler import (payload_interactivo_lista)
from app.services.whatsapp_service import recuperarContraseniaCel
from dotenv import load_dotenv

load_dotenv()
    
class GenerarCodigoHandler(BaseHandler):
    """Handler para generar codigo"""
    def __init__(self, msg_handler=None):
        super().__init__()
        self.msg_handler = msg_handler  # Guarda la referencia

    def get_context_name(self) -> str:
        return "agente"

    def get_priority(self) -> int:
        return 10  # Alta prioridad

    async def can_handle(self, texto: str, numero: str, user_state: dict) -> bool:
        texto_lower = texto.strip().lower()
        keywords = ["agente","necesito"]
        return any(keyword in texto_lower for keyword in keywords)

    async def handle_message(self, texto: str, numero: str, name: str, msg_id: str) -> List[Dict[str, Any]]:
        #await set_estado_usuario(numero, {"contexto": "codigo", "estado": "codigo", "ci": "", "mail": ""})
        dataList = []
        spinner = await crear_payload_texto(numero, "⏳ Estamos verificando tus datos...")
        dataList.append(spinner)
        ci = ''
        try:
            partes = texto.split('*')
            ci = partes[1] #'4781780'
        except Exception as error:
            return "❌ no existe ci"
        print("--ci--",ci)
        data = await self.consumirServico(numero, ci,name)
        payList = self._payload_custom_menu(numero, data)
        dataList.append(payList)
        await set_estado_usuario(numero, {"contexto": "", "estado": ""})
        return dataList
    
    def _payload_custom_menu(self, numero: str, mensaje: str) -> dict:
        seccion = self.msg_handler.build_seccion("🚀 Servicios Disponibles")
        secciones = [seccion]
        btn_lbl = "Ver servicios"
        return payload_interactivo_lista(numero, mensaje, secciones, btn_lbl)
    
    async def consumirServico(self, numero: str, ci: str,name: str) -> str:
        try:
            #numero = "73232817"
            respuesta = await recuperarContraseniaCel({"usuario": ci , "celular": numero})
            print("repuesta",respuesta)
            mensaje = f"""Hola {name} 
            Tu solicitud para restablecer la contraseña se ha procesado con éxito. 
            Aquí tienes tu *código* *{str(respuesta["success"]["PIN:"])}* 🔐 
            Por seguridad, este código es personal y temporal — úsalo solo para completar el proceso de recuperación de tu cuenta. 
            ¿Puedo ayudarte con algo más? 😊"""
            return mensaje


        except Exception as error:
            print(f"❌ hubo un error en el servicio: {error}")
            return "❌ hubo un error en el servicio."
