import os
from typing import List, Dict, Any
from .base_handler import BaseHandler
from app.services.utils.utils_handler import (payload_interactivo_lista, crear_payload_exitbtn, mail_valido, ci_valido, crear_payload_texto, ofuscar_correo)
from app.database.database import set_estado_usuario, get_estado_usuario
from app.services.whatsapp_service import recuperar_pin_ciudadano
from dotenv import load_dotenv

load_dotenv()
    
class CiudadanoHandler(BaseHandler):
    """Handler para 100 Jueves"""
    def __init__(self, msg_handler=None):
        super().__init__()
        self.msg_handler = msg_handler  # Guarda la referencia
        
    def get_context_name(self) -> str:
        return "ciudadano"

    def get_priority(self) -> int:
        return 10  # Alta prioridad

    async def can_handle(self, texto: str, numero: str, user_state: dict) -> bool:
        texto_lower = texto.strip().lower()
        keywords = ["ciudadano", "usac", "atencion"]
        return any(keyword in texto_lower for keyword in keywords)
    
    async def handle_message(self, texto: str, numero: str, name: str, msg_id: str) -> List[Dict[str, Any]]:
        dataList = []
        payload = crear_payload_texto(numero, "💳 Contáctate atención ciudadana!\nhttps://wa.me/59162431259", True)
        payList = self._payload_custom_menu(numero,"🤖AMI - Servicios Disponibles")  
        dataList.append(payload) 
        dataList.append(payList)  
        # Limpia el contexto para que vuelva al menú principal en el siguiente mensaje
        await set_estado_usuario(numero, {"contexto": "", "estado": "", "ci": "", "mail": ""})
        return dataList
    
    def _payload_custom_menu(self, numero: str, mensaje: str) -> dict:
        seccion = self.msg_handler.build_seccion("🚀 Servicios Disponibles") #INVOCA A SERVICIO DE msg_handler  -"handler":IgobHandler(self)-
        secciones = [seccion]
        btn_lbl = "Ver servicios"
        return payload_interactivo_lista(numero, mensaje, secciones, btn_lbl)