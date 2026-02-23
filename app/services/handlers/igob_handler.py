import os
from typing import List, Dict, Any
from .base_handler import BaseHandler
from app.services.utils.utils_handler import (
    payload_interactivo_lista, 
    payload_interactivo_boton,
    crear_payload_exitbtn, 
    mail_valido, 
    ci_valido, 
    crear_payload_texto, 
    ofuscar_correo, 
    crear_payload_texto_url)
from app.database.database import set_estado_usuario, get_estado_usuario
from app.services.whatsapp_service import recuperar_pin_ciudadano
from dotenv import load_dotenv

load_dotenv()

class IgobHandler(BaseHandler):
    """Handler para recuperación de contraseñas iGOB"""
    def __init__(self, msg_handler=None):
        super().__init__()
        self.msg_handler = msg_handler  # Guarda la referencia
    
    def get_context_name(self) -> str:
        return "igob"
    
    def get_priority(self) -> int:
        return 10  # Alta prioridadd
    
    async def can_handle(self, texto: str, numero: str, user_state: dict) -> bool:
        """Detecta intenciones relacionadas con iGOB"""
        texto_lower = texto.strip().lower()
        keywords = ["igob", "contraseña", "password", "pin", "recuperar"]
        return any(keyword in texto_lower for keyword in keywords)
    
    async def handle_message(self, texto: str, numero: str, name: str, msg_id: str) -> List[Dict[str, Any]]:
        """Maneja todo el flujo de recuperación de contraseña iGOB"""
        dataList = []
        user_state = await get_estado_usuario(numero)
        estado = user_state.get("estado", "") if user_state else ""
        ci = user_state.get("ci") if user_state else None
        
        # ✅ Cancelar proceso
        if texto.strip().lower() == "salir":
            await set_estado_usuario(numero, {"contexto": "", "estado": "", "ci": "", "mail": ""})
            mensaje = ( f"☺ Está bien, no hay problema. \n"
                     "🔔Puedes hacerlo en cualquier momento desde este chat.\n"
                     "¿Puedo ayudarte con algo más?")
            payload = self._payload_custom_menu(numero, mensaje)
            dataList.append(payload)
            return dataList
        
        # ✅ Estado inicial: mostrar información y pedir confirmación
        if estado == "":
            await set_estado_usuario(numero, {"contexto": "igob", "estado": "confirmar", "ci": "", "mail": ""})
            payload = self._mensaje_igob_pass_recovery(numero)
            #payload["to"] = numero
            dataList.append(payload)
            
        # ✅ Confirmación recibida: pedir CI
        elif estado == "confirmar" and texto.strip().lower() == "recuperar":
            await set_estado_usuario(numero, {"contexto": "igob", "estado": "ci", "ci": "", "mail": ""})
            payload = crear_payload_exitbtn(numero, "Por favor, indícame tu número de carnet de identidad (C.I.):", "salir", "Cancelar")
            dataList.append(payload)
            
        # ✅ Esperando CI
        elif estado == "ci":
            if ci_valido(texto):
                await set_estado_usuario(numero, {"contexto": "igob", "estado": "mail", "ci": texto, "mail": ""})
                payload = crear_payload_exitbtn(numero, "Ahora, por favor, ¿Cuál es tu correo electrónico registrado en iGOB?", "salir", "Cancelar")
            else:
                cuerpo = ("🚫 El número de C.I. que ingresaste parece incorrecto o tiene un formato no válido. Solo se admiten números y debe tener un mínimo de 5 dígitos, vamos a intentarlo otra vez.\n"
                          "Por favor, cuál es tu tu *número de carnet de identidad* (C.I.):")
                payload = crear_payload_exitbtn(numero, cuerpo, "salir", "Cancelar")
            dataList.append(payload)
            
        # ✅ Esperando email
        elif estado == "mail" and ci:
            if mail_valido(texto):
                # Spinner
                spinner = crear_payload_texto(numero, "⏳Estamos verificando tus datos...")
                dataList.append(spinner)
                
                # Procesar recuperación
                await set_estado_usuario(numero, {"contexto": "", "estado": "", "ci": "", "mail": ""})
                data = await recuperar_pin_ciudadano({"usuario": ci, "correo": texto})
                msg = self._generate_recovery_message(data, texto)
                if msg == "SIN-REGISTRO":
                    cuerpo = (f"❌ El número de Cédula de Identidad (C.I.) que proporcionaste no se encuentra registrado en iGOB. *No estás registrado en la plataforma iGOB* \n"
                              f"👉 Si quieres utilizar nuestros servicios online es obligatorio que primero estés registrado en la plataforma iGOB.\n" )
                    url = os.getenv("IGOB_REGISTER_URL", "https://igob247.lapaz.bo/app/view/autenticacion/partials/registro_.html")
                    url_lbl = "Registrarme en iGOB"
                    pldUrl = crear_payload_texto_url(numero, cuerpo, url, url_lbl) #
                    dataList.append(pldUrl)
                    msg = "¿Puedo ayudarte con algo más?"
                #payload = crear_payload_exitbtn(numero, msg, "hola", "Volver al inicio")
                payload = self._payload_custom_menu(numero, msg)
            else:
                cuerpo = ("🚫 El correo electrónico que ingresaste parece incorrecto o tiene un formato no válido. Asegúrate de que tenga un formato correcto (por ejemplo,usuario@dominio.com).\n"
                          "Vamos a intentarlo otra vez, ¿Cual es tu *correo eletrónico registrado en iGOB*?")
                payload = crear_payload_exitbtn(numero, cuerpo, "salir", "Cancelar")
            dataList.append(payload)
            
        else:
            payload = crear_payload_texto(numero, "🙂Por favor debes seleccionar una opción para poder continuar.")
            dataList.append(payload)
            
        return dataList
    
    def _mensaje_igob_pass_recovery(self, numero) -> dict:
        support_phone = os.getenv("SUPPORT_PHONE", "155")
        mensaje = (f"¡Vamos a ayudarte a recuperar tu contraseña de iGOB!😊\n"
                    "Antes de continuar es importante que sepas lo siguiente:\n"
                    "⚠ Debes *tener un correo electrónico registrado* previamente en iGOB\n"
                    f"👉 Si no lo recuerdas comunícate con el {support_phone}, para que te ayuden a recuperar tu correo y/o contraseña.\n"
                    "¿Continuamos?")
        botones = [ {"type": "reply", "reply": {"id": "recuperar", "title": "Si, continuar"}},
                    {"type": "reply", "reply": {"id": "salir", "title": "Cancelar"}} ]
        return payload_interactivo_boton(numero, mensaje, botones)
    
    def _generate_recovery_message(self, data: Dict, correo: str) -> str:
        """Genera mensaje según resultado de recuperación"""
        if data.get("success"):
            return (f"✅ ¡Todo correcto!\n"
                   f"Te enviamos tu nueva CONTRASEÑA al correo electrónico [{ofuscar_correo(correo)}].\n"
                   f"Por favor, revisa tu bandeja de entrada y también la carpeta de spam. ¿Puedo ayudarte con algo más?")
        
        error = data.get("error", {})
        support_phone = os.getenv("SUPPORT_PHONE", "155")
        
        if error.get("usuario") is None and "usuario" in error:
            return "SIN-REGISTRO"
        elif error.get("usuario") is True and error.get("correo") is None:
            return (f"✅ Hemos encontrado tu número de C.I., parece que no tienes un correo electrónico real registrado en iGOB o si estás acá puede ser que no lo recuerdes.\n"
                   f"👉 Si quieres utilizar nuestros servicios online comunícate con el {support_phone}, para que te ayuden a recuperar tu correo y/o contraseña.")
        elif error.get("usuario") is True and error.get("correo") is False:
            return (f"✅ Hemos encontrado tu número de C.I., pero el correo electrónico que ingresaste no coincide con el registrado en iGOB.\n"
                   f"❓ Si es que no lo recuerdas, comunícate con el {support_phone}, para que te ayuden a recuperarlo.")
        elif error.get("no_service") is True:
            return (f"❌ El servicio de recuperación de contraseña de iGOB no está disponible en este momento. "
                   f"Por favor, inténtalo más tarde o comunícate con el {support_phone} para obtener asistencia.")
        
        return "❌ Ocurrió un error inesperado. Por favor, inténtalo más tarde."

    def _payload_custom_menu(self, numero: str, mensaje: str) -> dict:
        seccion = self.msg_handler.build_seccion("🚀 Servicios Disponibles") #INVOCA A SERVICIO DE msg_handler  -"handler":IgobHandler(self)-
        secciones = [seccion]
        btn_lbl = "Ver servicios"
        return payload_interactivo_lista(numero, mensaje, secciones, btn_lbl)
