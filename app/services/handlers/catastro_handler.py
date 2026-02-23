import os
import re
from typing import List, Dict, Any

from app.services.utils.utils_handler import payload_interactivo_lista
from .base_handler import BaseHandler
from app.database.database import set_estado_usuario, get_estado_usuario
from app.services.whatsapp_service import consulta_tramite, recuperar_pin_ciudadano
from dotenv import load_dotenv

import datetime
from babel.dates import format_date

from app.services.whatsapp_template import (
    crear_payload_button,
    crear_payload_button_aux,
    crear_payload_lista,
    crear_payload_texto,
    mensaje_stiker
)

load_dotenv()

class CatastroHandler(BaseHandler):
    """Handler CATASTRO"""
    def __init__(self, msg_handler=None):
        super().__init__()
        self.msg_handler = msg_handler  # Guarda la referencia
        #print(self.msg_handler)
    
    def get_context_name(self) -> str:
        return "catastro"
    
    def get_priority(self) -> int:
        return 10  # Alta prioridad
    
    async def can_handle(self, texto: str, numero: str, user_state: dict) -> bool:
        """Detecta intenciones relacionadas con CATASTRO"""
        texto_lower = texto.strip().lower()
        keywords = ["catastro", "catastral", "catastro-a", "catastro-busca-tramite","catastro-cancelar"]
        return any(keyword in texto_lower for keyword in keywords)
    
    async def handle_message(self, texto: str, numero: str, name: str, msg_id: str) -> List[Dict[str, Any]]:
        """Maneja todo el flujo de CATASTRO"""
        dataList = []
        user_state = await get_estado_usuario(numero)
        estado = user_state.get("estado", "") if user_state else ""
        
        # ✅ Cancelar proceso
        if texto.strip().lower() == "salir":
            await set_estado_usuario(numero, {"contexto": "", "estado": ""})
            #payload = await crear_payload_texto(numero,"❌ Proceso cancelado. ¿En qué más puedo ayudarte?")

            #dataList = []
            msg = ("😌 Está bien, no hay problema.\n"
                "🔔 Puedes hacerlo en cualquier momento desde este chat.\n"
                "¿Puedo ayudarte con algo más?\n"
                "*Selecciona una de las opciones siguientes:*")
            payList = self._payload_custom_menu(numero, msg)
            dataList.append(payList)

            """payload = await crear_payload_lista(
                numero,
                "😌 Está bien, no hay problema.\n"+
                "🔔 Puedes hacerlo en cualquier momento desde este chat.\n"+
                "¿Puedo ayudarte con algo más?",
                self._opciones_inicio(),
                '',
                '*Selecciona una de las opciones siguientes:*',
                'Ver opciones'
            )
            dataList.append(payload)"""
            return dataList
        
        # ✅ Estado inicial: mostrar información y pedir confirmación
        if estado == "":
            #await set_estado_usuario(numero, {"contexto": "catastro", "estado": "catastro-a"})
            stiker = await mensaje_stiker(numero,"653098227752705")
            dataList.append(stiker)
            """ 
            payload = await crear_payload_lista(
                numero,
                "*👋¡Hola! Bienvenido al servicio de atención al cliente de Catastro.* \n😊¿En qué puedo ayudarte hoy?",
                self._opciones_catastro(),
                '',
                '*Selecciona una de las opciones siguientes:*',
                'Ver opciones'
            )
            """
            #payload = await crear_payload_texto(numero,"*👋¡Hola! Bienvenido al servicio de atención al cliente de Catastro.*")
            #dataList.append(payload)
        #elif estado == "catastro-a":
            await set_estado_usuario(numero, {"contexto": "catastro", "estado": "catastro-a-a"})
            payload = await crear_payload_button(numero,"¡Hola 😊 "+name+", bienvenido, al servicio seguimiento trámite catastral, por favor ingresa el número de trámite:","","salir","Cancelar")
            dataList.append(payload)
            
        elif texto in self.msg_handler.handlers.keys():
            await set_estado_usuario(numero, {"contexto": "", "estado": "","numero-tramite": ""})
            return await self.msg_handler.process_message(texto,numero,name,msg_id)
            
        elif estado == "catastro-a-a":
            if self._valido(texto):
                await set_estado_usuario(numero, {"contexto": "catastro", "estado": "catastro-busca-tramite","numero-tramite": texto})
                payload = await crear_payload_button(numero,"Por favor ingresa la contraseña del trámite:","","salir","Cancelar")
            else:
                payload = await crear_payload_button(numero,"🚫 El número de trámite que ingresaste parece incorrecto o tiene un formato no válido, ingresa un minimo de 3 dígitos, vamos a intentarlo otra vez, por favor ingresa el número de trámite:","","salir","Cancelar")
            dataList.append(payload)
        
        elif estado == "catastro-busca-tramite":
            spinner = await crear_payload_texto(numero, "⏳Estamos verificando tus datos...")
            dataList.append(spinner)
            if self._valido(texto):

                user_state = await get_estado_usuario(numero)
                numero_tramite = user_state.get("numero-tramite") if user_state else None
                
                #await set_estado_usuario(numero, {"contexto": "catastro", "estado": "catastro-a"})
                await set_estado_usuario(numero, {"contexto": "catastro", "estado": ""})
                data = await self.procesar_tramite(numero_tramite,texto)
                payload = await crear_payload_button_aux(numero,data,"","catastro","Nueva consulta")
                dataList.append(payload)
            else:
                payload = await crear_payload_button(numero,"🚫 La contraseña que ingresaste parece incorrecto o tiene un formato no válido, ingresa un minimo de 3 dígitos, vamos a intentarlo otra vez, por favor ingresa la contraseña del trámite:","","salir","Cancelar")
                dataList.append(payload)

        elif estado == "catastro-cancelar":
            await set_estado_usuario(numero, {"contexto": "", "estado": ""})
            payload = await crear_payload_texto(numero,"❌ Hubo un error. Volvamos al inicio.")
            payload["to"] = numero
            dataList.append(payload)
            
        else:
            # Estado no reconocido, reiniciar
            await set_estado_usuario(numero, {"contexto": "", "estado": ""})
            payload = await crear_payload_texto(numero,"❌ Hubo un error. Volvamos al inicio.")
            payload["to"] = numero
            dataList.append(payload)
            
        return dataList
    def _opciones_inicio(self)-> dict:
        campos = [
                    {
                        "title": "🚀 Servicios Disponibles",
                        "rows": [
                            {
                                "id": "igob",
                                "title": "Recupera contraseña IGOB",
                                "description": "¿Olvidaste tu clave? Recupérala en segundos sin filas ni esperas."
                            },
                            {
                                "id": "tramites",
                                "title": "Seguimiento de trámites",
                                "description": "Consulta en tiempo real el estado de tus trámites municipales"
                            },
                            {
                                "id": "catastro",
                                "title": "Información catastral",
                                "description": "Requisitos, horarios de atención y contactos directos para propiedades"
                            },
                            {
                                "id": "hospitales",
                                "title": "Hospitales municipales",
                                "description": "Ubicaciones, horarios de atención, servicios médicos disponibles"
                            },
                            {
                                "id": "ciudadano",
                                "title": "Información ciudadana",
                                "description": "Puntos de atención, horarios de servicios municipales y documentos"
                            },
                            {
                                "id": "peludos",
                                "title": "Atención veterinaria",
                                "description": "Agenda consultas, vacunas o esterilizaciones para tus peluditos"
                            },
                            {
                                "id": "100_jueves",
                                "title": "100 Jueves de Acción",
                                "description": "¡Solicita mejoras para tu barrio! Como limpieza de áreas verdes."
                            }
                            
                        ],
                    }
                ]
        return campos
    def _opciones_catastro(self) -> dict:
        campos = [
            {
                "title": "Opciones",
                "rows": [
                    {
                        "id": "catastro-a",
                        "title": "Opción (A)",
                        "description": "Consulta tu trámite",
                    },
                    {
                        "id": "catastro-b",
                        "title": "Opción (B)",
                        "description": "Requisitos y para trámites en catastro.",
                    },
                    {
                        "id": "catastro-c",
                        "title": "Opción (C)",
                        "description": "Puntos y horarios de atención",
                    },
                    {
                        "id": "catastro-d",
                        "title": "Opción (D)",
                        "description": "Preguntas Frecuentes",
                    },
                    {
                        "id": "catastro-e",
                        "title": "Opción (E)",
                        "description": "Contactos direcciones",
                    },
                ],
            }
        ]
        return campos
    
    def _payload_custom_menu(self, numero: str, mensaje: str) -> dict:
        seccion = self.msg_handler.build_seccion("🚀 Servicios Disponibles") #INVOCA A SERVICIO DE msg_handler  -"handler":IgobHandler(self)-
        secciones = [seccion]
        btn_lbl = "Ver servicios"
        return payload_interactivo_lista(numero, mensaje, secciones, btn_lbl)    

    def _valido(self, texto: str) -> bool:
        patron = r"^[a-zA-Z0-9\-]+$"
        return (
            re.fullmatch(patron, texto) is not None and
            len(texto) >= 3 and
            not self.contiene_emojis(texto)
        )

    def contiene_emojis(self, texto: str) -> bool:
        emoji_pattern = re.compile(
            "[" 
            "\U0001F600-\U0001F64F"  # Emoticonos
            "\U0001F300-\U0001F5FF"  # Símbolos y pictogramas
            "\U0001F680-\U0001F6FF"  # Transporte y mapas
            "\U0001F1E0-\U0001F1FF"  # Banderas
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )
        return emoji_pattern.search(texto) is not None

    async def procesar_tramite(self,numero_tramite: str,contra_tramite: str) -> str:
        try:
            respuesta = await consulta_tramite({"numero": numero_tramite, "contra": contra_tramite})
            campos = respuesta
            data_tramite = ''
            tipo_ubicacion = True
            if not campos.get("estado"):
                return "❌ No se logró identificar el trámite, verifica si el número o contraseña del trámite son los correctos y vuelve a intentarlo."
            proximo_paso = ''
            comentarios_adicionales = ''
            historial = campos['data']['historial']
            data_principal = campos['data']['data_principal']
            cantidad = len(historial) - 1
            cantidad_primera_posicion = cantidad - 1
            cantidad_segunda_posicion = cantidad - 2
            ubicacion_tramite = ""
            fecha_modificacion = ""
            remitente = data_principal.get('remitente', '').strip()
            data_tramite += f"*{remitente}*, aquí tienes el estado de tu trámite Nº *{numero_tramite}*\n"
            nodo_actual = f"{historial[cantidad]['nodo_activo']['nodo']} ({historial[cantidad]['nodo_activo']['uo_sigla']})"
            nodos_validos = {
                'PLATAFORMA INTEGRAL CAMACHO (USAC)',
                'PLATAFORMA INTEGRAL SUR (USAC)',
                'PLATAFORMA INTEGRAL MIRAFLORES (USAC)',
                'ASISTENTE ADMINISTRATIVO (URSC)',
                'APOYO ADMINISTRATIVO (UANI)',
                'APOYO ADMINISTRATIVO (URSC)',
            }
            if nodo_actual in nodos_validos:
                nodo_actual = f"{historial[cantidad]['nodo_activo']['nodo']} ({historial[cantidad]['nodo_activo']['uo_sigla']})"
                nodos_integrales = {
                    'PLATAFORMA INTEGRAL CAMACHO (USAC)',
                    'PLATAFORMA INTEGRAL SUR (USAC)',
                    'PLATAFORMA INTEGRAL MIRAFLORES (USAC)',
                }
                if nodo_actual in nodos_integrales:
                    if historial[cantidad]['estado'] == 'RECIBIDO':
                        data_tramite = data_tramite + '🔴 Tu trámite fue recepcionado y sera asignado a un técnico en la unidad de catastro.' + '\n'
                        proximo_paso = 'Tu documentación será asignada a un técnico procesador para su revisión en la unidad de catastro.'
                        comentarios_adicionales = 'Te avisaremos cuando tu trámite esté en proceso.'
                        ubicacion_tramite = historial[cantidad]['nodo_activo']['nombre_nodo'] + " de la " + historial[cantidad]['nodo_activo']['uo_sigla_descripcion'] + " (" + historial[cantidad]['nodo_activo']['uo_sigla'] + ")"
                        fecha_modificacion = historial[cantidad]['nodo_activo']['fecha_iso']
                    else:
                        data_tramite = data_tramite + '🔴 Tu trámite fue recepcionado y sera asignado a un técnico en la unidad de catastro.' + '\n'
                        proximo_paso = 'Tu documentación será asignada a un técnico procesador para su revisión en la unidad de catastro.'
                        comentarios_adicionales = 'Te avisaremos cuando tu trámite esté en proceso.'
                        ubicacion_tramite = historial[cantidad_primera_posicion]['nodo_activo']['nombre_nodo'] + " de la " + historial[cantidad_primera_posicion]['nodo_activo']['uo_sigla_descripcion'] + " (" + historial[cantidad_primera_posicion]['nodo_activo']['uo_sigla'] + ")"
                        fecha_modificacion = historial[cantidad_primera_posicion]['nodo_activo']['fecha_iso']
                    
                else:
                    nodo_primera_pos = f"{historial[cantidad_primera_posicion]['nodo_activo']['nodo']} ({historial[cantidad_primera_posicion]['nodo_activo']['uo_sigla']})"
                    nodo_actual = f"{historial[cantidad]['nodo_activo']['nodo']} ({historial[cantidad]['nodo_activo']['uo_sigla']})"
                    nodos_integrales = {
                        'PLATAFORMA INTEGRAL CAMACHO (USAC)',
                        'PLATAFORMA INTEGRAL SUR (USAC)',
                        'PLATAFORMA INTEGRAL MIRAFLORES (USAC)',
                    }
                    nodos_asistentes = {
                        'ASISTENTE ADMINISTRATIVO (URSC)',
                        'ASISTENTE ADMINISTRATIVO (UANI)',
                        'APOYO ADMINISTRATIVO (URSC)',
                        'APOYO ADMINISTRATIVO (UANI)',
                    }
                    if nodo_primera_pos in nodos_integrales and nodo_actual in nodos_asistentes:
                        if historial[cantidad]['estado'] == 'RECIBIDO':
                            data_tramite = data_tramite + '🔴 Tu trámite fue recepcionado y sera asignado a un técnico en la unidad de catastro.' + '\n'
                            proximo_paso = 'Tu documentación será asignada a un técnico procesador para su revisión en la unidad de catastro.'
                            comentarios_adicionales = 'Te avisaremos cuando tu trámite esté en proceso.'
                            ubicacion_tramite = historial[cantidad]['nodo_activo']['nombre_nodo'] + " de la " + historial[cantidad]['nodo_activo']['uo_sigla_descripcion'] + " (" + historial[cantidad]['nodo_activo']['uo_sigla'] + ")"
                            fecha_modificacion = historial[cantidad]['nodo_activo']['fecha_iso']
                        else:
                            data_tramite = data_tramite + '🔴 Tu trámite fue recepcionado y sera asignado a un técnico en la unidad de catastro.' + '\n'
                            proximo_paso = 'Tu documentación será asignada a un técnico procesador para su revisión en la unidad de catastro.'
                            comentarios_adicionales = 'Te avisaremos cuando tu trámite esté en proceso.'
                            ubicacion_tramite = historial[cantidad_primera_posicion]['nodo_activo']['nombre_nodo'] + " de la " + historial[cantidad_primera_posicion]['nodo_activo']['uo_sigla_descripcion'] + " (" + historial[cantidad_primera_posicion]['nodo_activo']['uo_sigla'] + ")"
                            fecha_modificacion = historial[cantidad_primera_posicion]['nodo_activo']['fecha_iso']
                    else:
                        nodo_actual = f"{historial[cantidad]['nodo_activo']['nodo']} ({historial[cantidad]['nodo_activo']['uo_sigla']})"
                        nodo_primero = f"{historial[cantidad_primera_posicion]['nodo_activo']['nodo']} ({historial[cantidad_primera_posicion]['nodo_activo']['uo_sigla']})"
                        nodo_segundo = f"{historial[cantidad_segunda_posicion]['nodo_activo']['nodo']} ({historial[cantidad_segunda_posicion]['nodo_activo']['uo_sigla']})"
                        grupo_actual = {
                            'ASISTENTE ADMINISTRATIVO (URSC)',
                            'APOYO ADMINISTRATIVO (UANI)'
                        }

                        grupo_primero = {
                            'ASISTENTE ADMINISTRATIVO (URSC)',
                            'APOYO ADMINISTRATIVO (UANI)',
                            'APOYO ADMINISTRATIVO (URSC)'
                        }

                        grupo_segundo = {
                            'PLATAFORMA INTEGRAL CAMACHO (USAC)',
                            'PLATAFORMA INTEGRAL SUR (USAC)',
                            'PLATAFORMA INTEGRAL MIRAFLORES (USAC)'
                        }
                        if (
                            nodo_actual in grupo_actual and
                            nodo_primero in grupo_primero and
                            nodo_segundo in grupo_segundo
                        ):
                            if historial[cantidad]['estado'] == 'RECIBIDO':
                                data_tramite = data_tramite + '🔴 Tu trámite fue recepcionado y sera asignado a un técnico en la unidad de catastro.' + '\n'
                                proximo_paso = 'Tu documentación será asignada a un técnico procesador para su revisión en la unidad de catastro.'
                                comentarios_adicionales = 'Te avisaremos cuando tu trámite esté en proceso.'
                                ubicacion_tramite = historial[cantidad]['nodo_activo']['nombre_nodo'] + " de la " + historial[cantidad]['nodo_activo']['uo_sigla_descripcion'] + " (" + historial[cantidad]['nodo_activo']['uo_sigla'] + ")"
                                fecha_modificacion = historial[cantidad]['nodo_activo']['fecha_iso']
                            else:
                                data_tramite = data_tramite + '🔴 Tu trámite fue recepcionado y sera asignado a un técnico en la unidad de catastro.' + '\n'
                                proximo_paso = 'Tu documentación será asignada a un técnico procesador para su revisión en la unidad de catastro.'
                                comentarios_adicionales = 'Te avisaremos cuando tu trámite esté en proceso.'
                                ubicacion_tramite = historial[cantidad_primera_posicion]['nodo_activo']['nombre_nodo'] + " de la " + historial[cantidad_primera_posicion]['nodo_activo']['uo_sigla_descripcion'] + " (" + historial[cantidad_primera_posicion]['nodo_activo']['uo_sigla'] + ")"
                                fecha_modificacion = historial[cantidad_primera_posicion]['nodo_activo']['fecha_iso']
                        else:
                            if historial[cantidad]['estado'] == 'RECIBIDO':
                                data_tramite = data_tramite + '🟡 Tu trámite esta en proceso.' + '\n'
                                proximo_paso = 'Tu documentación pasara a ser revisada y validada.'
                                comentarios_adicionales = 'Te avisaremos cuando tu tramite haya finalizado.'
                                ubicacion_tramite = historial[cantidad]['nodo_activo']['nombre_nodo'] + " de la " + historial[cantidad]['nodo_activo']['uo_sigla_descripcion'] + " (" + historial[cantidad]['nodo_activo']['uo_sigla'] + ")"
                                fecha_modificacion = historial[cantidad]['nodo_activo']['fecha_iso']
                            else:
                                data_tramite = data_tramite + '🟡 Tu trámite esta en proceso.' + '\n'
                                proximo_paso = 'Tu documentación pasara a ser revisada y validada.'
                                comentarios_adicionales = 'Te avisaremos cuando tu tramite haya finalizado.'
                                ubicacion_tramite = historial[cantidad_primera_posicion]['nodo_activo']['nombre_nodo'] + " de la " + historial[cantidad_primera_posicion]['nodo_activo']['uo_sigla_descripcion'] + " (" + historial[cantidad_primera_posicion]['nodo_activo']['uo_sigla'] + ")"
                                fecha_modificacion = historial[cantidad_primera_posicion]['nodo_activo']['fecha_iso']
            else:
                nodo_actual = f"{historial[cantidad]['nodo_activo']['nodo']} ({historial[cantidad]['nodo_activo']['uo_sigla']})"
                nodos_finalizados_observados = {
                    'FINALIZADOS PLATAFORMA INTEGRAL CAMACHO (USAC)',
                    'OBSERVADOS PLATAFORMA INTEGRAL CAMACHO (USAC)',
                    'FINALIZADOS PLATAFORMA INTEGRAL SUR (USAC)',
                    'OBSERVADOS PLATAFORMA INTEGRAL SUR (USAC)',
                    'FINALIZADOS PLATAFORMA INTEGRAL MIRAFLORES (USAC)',
                    'OBSERVADOS PLATAFORMA INTEGRAL MIRAFLORES (USAC)',
                    'PARA ENTREGA AL CIUDADANO FINALIZADOS DDAT SMP (UAPCT)'
                }
                if nodo_actual in nodos_finalizados_observados:
                    if historial[cantidad]['estado'] == 'RECIBIDO':
                        data_tramite += '🟢 Tu trámite ha finalizado.\n'
                        proximo_paso = 'Recoger los resultados del tramite.'
                        informacion_adicional = (
                            "✅ *Información útil:*\n"
                            "*1. Atención:* 08:15hrs. a 17:30hrs. (continuo).\n"
                            "*2. Documentos:* de forma personal (el titular ) con el C.I., en caso de una tercera persona como un apoderado presentar el poder notarial y su C.I.\n"
                            "⚠️ *Prevenir* si en 90 días no recoge el trámite el mismo será enviado a archivo, donde tendrá que solicitar su desarchivo mediante una nota para poder recoger su trámite."
                        )
                        nodo_nombre = historial[cantidad]['nodo_activo']['nodo'].upper()
                        plataformas = {
                            'CAMACHO': {
                                'mensaje': "Pasar por la Plataforma Integral de Atención Ciudadana Camacho - PIAC CAMACHO : Av. Camacho, Centro Comercial Camacho Nivel 1",
                                'mapa': "https://maps.app.goo.gl/XQtRE17M7SnFHT596"
                            },
                            'MIRAFLORES': {
                                'mensaje': "Pasar por la Plataforma Integral de Atención Ciudadana Miraflores - PIAC MIRAFLORES : Calle Chichas esq. Juan de Vargas  Edificio ESPRA  PB, Z. Miraflores",
                                'mapa': "https://maps.app.goo.gl/DqS8UsMUqbxmixjR9"
                            },
                            'SUR': {
                                'mensaje': "Pasar por la Plataforma Integral de Atención Ciudadana Sur - PIAC SUR : Av. Gral. José Ballivián Nº720, entre calles 13 y 14 Calacoto. Planta Baja Edif. ATLANTA",
                                'mapa': "https://maps.app.goo.gl/513ba6Yy9iusifVo9"
                            }
                        }
                        comentarios_adicionales = ""
                        for clave, datos in plataformas.items():
                            if clave in nodo_nombre:
                                comentarios_adicionales = f"{datos['mensaje']}\n*Como llegar:* {datos['mapa']}"#{informacion_adicional}"
                                break
                        if comentarios_adicionales is None:
                            comentarios_adicionales = f"Pasar por la plataforma de atención GAMLP donde inició su trámite.\n"#{informacion_adicional}"
                        ubicacion_tramite = f"{historial[cantidad]['nodo_activo']['nombre_nodo']} de la {historial[cantidad]['nodo_activo']['uo_sigla_descripcion']} ({historial[cantidad]['nodo_activo']['uo_sigla']})"
                        fecha_modificacion = historial[cantidad]['nodo_activo']['fecha_iso']
                    else:
                        if historial[cantidad]['estado'] == 'CERRADO':
                            data_tramite = data_tramite + '⚪ *Estado Actual*: ' + '*Cerrado*' + '\n'
                            proximo_paso = 'Este tramite esta cerrado.'
                            comentarios_adicionales = 'Este tramite esta cerrado.'
                            ubicacion_tramite = historial[cantidad]['nodo_activo']['nombre_nodo'] + " de la " + historial[cantidad]['nodo_activo']['uo_sigla_descripcion'] + " (" + historial[cantidad]['nodo_activo']['uo_sigla'] + ")"
                            fecha_modificacion = historial[cantidad]['nodo_activo']['fecha_iso']
                            tipoUbicacion = False
                        else:
                            data_tramite = data_tramite + '🟡 Tu trámite esta en proceso.' + '\n'
                            proximo_paso = 'Tu documentación pasara a ser revisada y validada.'
                            comentarios_adicionales = 'Te avisaremos cuando tu tramite haya finalizado.'
                            ubicacion_tramite = historial[cantidad_primera_posicion]['nodo_activo']['nombre_nodo'] + " de la " + historial[cantidad_primera_posicion]['nodo_activo']['uo_sigla_descripcion'] + " (" + historial[cantidad_primera_posicion]['nodo_activo']['uo_sigla'] + ")"
                            fecha_modificacion = historial[cantidad_primera_posicion]['nodo_activo']['fecha_iso']
                else:
                    def obtener_nombre_nodo(item):
                        return f"{item['nodo']} ({item['uo_sigla']})"
                    plataformas_integrales = {
                        "PLATAFORMA INTEGRAL CAMACHO (USAC)",
                        "PLATAFORMA INTEGRAL SUR (USAC)",
                        "PLATAFORMA INTEGRAL MIRAFLORES (USAC)"
                    }

                    asistentes_o_apoyos = {
                        "ASISTENTE ADMINISTRATIVO (URSC)",
                        "APOYO ADMINISTRATIVO (UANI)",
                        "APOYO ADMINISTRATIVO (URSC)",
                        *plataformas_integrales
                    }
                    nodo_segunda = obtener_nombre_nodo(historial[cantidad_segunda_posicion]['nodo_activo'])
                    nodo_primera = obtener_nombre_nodo(historial[cantidad_primera_posicion]['nodo_activo'])
                    if nodo_segunda in plataformas_integrales and nodo_primera in asistentes_o_apoyos:
                        if historial[cantidad]['estado'] == 'RECIBIDO':
                            data_tramite = data_tramite + '🟡 Tu trámite esta en proceso.' + '\n'
                            proximo_paso = 'Tu documentación pasara a ser revisada y validada.'
                            comentarios_adicionales = 'Te avisaremos cuando tu tramite haya finalizado.'
                            ubicacion_tramite = historial[cantidad]['nodo_activo']['nombre_nodo'] + " de la " + historial[cantidad]['nodo_activo']['uo_sigla_descripcion'] + " (" + historial[cantidad]['nodo_activo']['uo_sigla'] + ")"
                            fecha_modificacion = historial[cantidad]['nodo_activo']['fecha_iso']
                        else:
                            data_tramite = data_tramite + '🔴 Tu trámite fue recepcionado y sera asignado a un técnico en la unidad de catastro.' + '\n'
                            proximo_paso = 'Tu documentación será asignada a un técnico procesador para su revisión en la unidad de catastro.'
                            comentarios_adicionales = 'Te avisaremos cuando tu trámite esté en proceso.'
                            ubicacion_tramite = historial[cantidad_primera_posicion]['nodo_activo']['nombre_nodo'] + " de la " + historial[cantidad_primera_posicion]['nodo_activo']['uo_sigla_descripcion'] + " (" + historial[cantidad_primera_posicion]['nodo_activo']['uo_sigla'] + ")"
                            fecha_modificacion = historial[cantidad_primera_posicion]['nodo_activo']['fecha_iso']
                    else:
                        if historial[cantidad]['estado'] == 'RECIBIDO':
                            data_tramite = data_tramite + '🟡 Tu trámite esta en proceso.' + '\n'
                            proximo_paso = 'Tu documentación pasara a ser revisada y validada.'
                            comentarios_adicionales = 'Te avisaremos cuando tu tramite haya finalizado.'
                            ubicacion_tramite = historial[cantidad]['nodo_activo']['nombre_nodo'] + " de la " + historial[cantidad]['nodo_activo']['uo_sigla_descripcion'] + " (" + historial[cantidad]['nodo_activo']['uo_sigla'] + ")"
                            fecha_modificacion = historial[cantidad]['nodo_activo']['fecha_iso']
                        else:
                            if historial[cantidad]['estado'] == 'CERRADO':
                                data_tramite = data_tramite + '⚪ *Estado Actual*: ' + '*Cerrado*' + '\n'
                                proximo_paso = 'Este tramite esta cerrado.'
                                comentarios_adicionales = 'Este tramite esta cerrado.'
                                ubicacion_tramite = historial[cantidad]['nodo_activo']['nombre_nodo'] + " de la " + historial[cantidad]['nodo_activo']['uo_sigla_descripcion'] + " (" + historial[cantidad]['nodo_activo']['uo_sigla'] + ")"
                                fecha_modificacion = historial[cantidad]['nodo_activo']['fecha_iso']
                                tipoUbicacion = False
                            else:
                                data_tramite = data_tramite + '🟡 Tu trámite esta en proceso.' + '\n'
                                proximo_paso = 'Tu documentación pasara a ser revisada y validada.'
                                comentarios_adicionales = 'Te avisaremos cuando tu tramite haya finalizado.'
                                ubicacion_tramite = historial[cantidad_primera_posicion]['nodo_activo']['nombre_nodo'] + " de la " + historial[cantidad_primera_posicion]['nodo_activo']['uo_sigla_descripcion'] + " (" + historial[cantidad_primera_posicion]['nodo_activo']['uo_sigla'] + ")"
                                fecha_modificacion = historial[cantidad_primera_posicion]['nodo_activo']['fecha_iso']
        
                data_tramite = data_tramite + '*-------------------------------------------* \n'
            
                asunto = campos['data']['data_principal'].get('asunto', '')
                data_tramite += f'📄 *Asunto*: {asunto}\n'
                        
                fecha_creacion = datetime.datetime.strptime(data_principal['fecha_creacion'], "%Y-%m-%dT%H:%M:%S.%fZ")
                fecha_literal = format_date(fecha_creacion.date(), format='full', locale='es')
                data_tramite += f"📆 *El Trámite ingresó*: {fecha_literal}\n"

                if fecha_modificacion is None:
                    data_tramite += '📆 *Última fecha de actualización fue*: El tramite aun no ha sido recibido\n'
                else:
                    fecha2 = datetime.datetime.strptime(fecha_modificacion, "%Y-%m-%dT%H:%M:%S.%fZ")
                    fecha_literal2 = format_date(fecha2.date(), format='full', locale='es')
                    data_tramite += f"📆 *Última fecha de actualización en*: {fecha_literal2}\n"            
                    
                if tipo_ubicacion:
                    data_tramite += f'📍 *El trámite se encuentra en*: {ubicacion_tramite}\n'
                    operador =  self.lo_tiene(historial[-1])
                    data_tramite += f'✅ *Lo tiene*: {operador}\n'
                try:
                    data_tramite += f'💬 {comentarios_adicionales} \n'
                except Exception:
                    pass

                data_tramite += '*Información útil:*\n'
                data_tramite += '1. Atención de 08:15hrs. a 17:30hrs (continuo).\n'
                data_tramite += '2. Para recoger el trámite, de forma personal el titular debe apersonarse con su carnet de identidad. En caso de una tercera persona, como un apoderado, debe presentar el poder notarial y su carnet de identidad.\n'
                #data_tramite += '*Prevenir*, si en 90 días no recoge el trámite será enviado a archivo, donde tendrá que solicitar su desarchivo mediante una nota para poder recoger su trámite.\n'
                #data_tramite += f'{informacion_adicional} \n'  LA CANTIDAD DE CARACTERES REBASA 1024, REVISAR!!!

                data_tramite += f"*Historial del trámite:* http://sitram247iconsulta.lapaz.bo/sigueTuTramite/view/autenticacion/?id={contra_tramite}{numero_tramite}"
            return data_tramite

        except Exception as error:
            print(f"❌ Error al consultar el trámite: {error}")
            return "❌ Error al consultar el trámite."
        
    def lo_tiene(self, current_state: dict) -> str:
        nodo = "activo"
        if current_state["estado"] == "ENTRANTE":
            nodo = "previo"
        return current_state[f"nodo_{nodo}"]["usuario_operador_nombre"]





#NUEVO
import re
from typing import List, Dict, Any

from app.services.handlers.base_handler import BaseHandler
from app.database.database import set_estado_usuario, get_estado_usuario
from app.services.whatsapp_template import (
    crear_payload_texto,
    crear_payload_button,
    crear_payload_button_aux,
    crear_payload_lista,      # 👈 IMPORTANTE: agregamos esta importación
    mensaje_stiker
)
from app.services.utils.utils_handler import payload_interactivo_lista
from app.services.handlers.catastro.menu_catastro import obtener_opciones_catastro
from app.services.handlers.catastro.A_consulta_tramite import flujo_opcion_a
from app.services.handlers.catastro.D_preguntas_frecuentes import manejar_preguntas_frecuentes


class CatastroHandler(BaseHandler):
    """Handler MENÚ CATASTRO"""

    def __init__(self, msg_handler=None):
        super().__init__()
        self.msg_handler = msg_handler

    def get_context_name(self) -> str:
        return "catastro"

    def get_priority(self) -> int:
        return 10

    async def can_handle(self, texto: Any, numero: str, user_state: dict) -> bool:
        texto_lower = self._extraer_texto_id(texto).strip().lower()
        keywords = ["catastro", "catastral"]
        estado = user_state.get("estado", "") if user_state else ""
        return estado.startswith("catastro") or any(keyword in texto_lower for keyword in keywords)

    async def handle_message(self, texto: Any, numero: str, name: str, msg_id: str) -> List[Dict[str, Any]]:
        dataList = []
        user_state = await get_estado_usuario(numero)
        estado = user_state.get("estado", "") if user_state else ""
        texto_real = self._extraer_texto_id(texto).strip().lower()

        # Salir al menú principal
        if texto_real == "inicio":
            await set_estado_usuario(numero, {"contexto": "", "estado": ""})
            msg = (
                "😌 Está bien, no hay problema.\n"
                "🔔 Puedes hacerlo en cualquier momento desde este chat.\n"
                "¿Puedo ayudarte con algo más?\n"
                "*Selecciona una de las opciones siguientes:*"
            )
            payList = self._payload_custom_menu(numero, msg)
            dataList.append(payList)
            return dataList
        
        # VOLVER A B) REQUISITOS
        if estado == "requisitos-catastro" and texto_real == "catastro-b":
            # Volver al menú principal de catastro
            mensaje = f"*👋 ¡Hola {name}!* te encuentras en la seccion de *información catastral.*\n Aquí podrás consultar los requisitos de trámites, horarios de atención, direcciones y más.\n 👉 Selecciona una de las opciones disponibles en información catastral para continuar:"
            opciones = obtener_opciones_catastro()

            opciones[0]["rows"].append({
                "id": "inicio",
                "title": "Volver al inicio",
                "description": "Regresar al menú principal"
            })

            payload = await crear_payload_lista(
                numero,
                mensaje,
                opciones,
                "",  # footer
                "",
                "Inf. Catastral"
            )
            await set_estado_usuario(numero, {"contexto": "catastro", "estado": "esperando-opcion"})
            dataList.append(payload)
            return dataList

        # Estado inicial → mostrar lista interactiva del menú catastral
        if estado == "":
            stiker = await mensaje_stiker(numero, "653098227752705")
            dataList.append(stiker)

            mensaje = f"*👋 ¡Hola {name}!* te encuentras en la seccion de *información catastral.*\n Aquí podrás consultar los requisitos de trámites, horarios de atención, direcciones y más.\n 👉 Selecciona una de las opciones disponibles en información catastral para continuar:"
            opciones = obtener_opciones_catastro()
            opciones[0]["rows"].append({
                "id": "inicio",
                "title": "Volver al inicio",
                "description": "Regresar al menú principal."
            })

            # Enviamos directamente la LISTA interactiva (no texto + botón)
            payload_lista = await crear_payload_lista(
                numero,
                mensaje,
                opciones,
                "",  # footer
                "",  # encabezado de la lista
                "Inf. Catastral"  # texto del botón
            )
            dataList.append(payload_lista)

            await set_estado_usuario(numero, {"contexto": "catastro", "estado": "esperando-opcion"})
            return dataList

        
        # 🔹 Derivar al flujo de la opción A (consulta de trámite catastral)
        if (
            estado.startswith("catastro-a")
            or estado.startswith("catastro-busca-tramite")
            or texto_real.startswith("catastro-a")
        ):
            user_state = await get_estado_usuario(numero)
            dataList = await flujo_opcion_a(texto_real, numero, user_state, name)
            return dataList

#  dataList = await flujo_opcion_a(texto_real, numero, user_state, name)

        # Opción B → requisitos
        if estado == "esperando-opcion" and texto_real == "catastro-b":
            from app.services.handlers.catastro.B_requisitos import manejar_requisitos_catastro
            respuesta = await manejar_requisitos_catastro(numero)
            dataList.extend(respuesta)
            return dataList
        
        # Opción B.1 → Certificado de registro
        if texto_real == "req-catastro-1":
            from app.services.handlers.catastro.B_1_Certificado_registro import manejar_certificado_registro
            respuesta = await manejar_certificado_registro(numero)
            dataList.extend(respuesta)
            return dataList
        # Volver desde el submenú "Certificado de registro" al menú de requisitos
        if estado == "certificado-opcion" and texto_real == "catastro-b":
            from app.services.handlers.catastro.B_requisitos import manejar_requisitos_catastro
            respuesta = await manejar_requisitos_catastro(numero)
            dataList.extend(respuesta)
            return dataList

        # B_1_1_Certificado_registro_PU.py
        if texto_real == "certificado-pu":
            from app.services.handlers.catastro.B_1_1_Certificado_registro_pu import manejar_certificado_pu
            respuesta = await manejar_certificado_pu(numero)
            dataList.extend(respuesta)
            return dataList
        # B_1_2_Certificado_ph.py
        if texto_real == "certificado-ph":
            from app.services.handlers.catastro.B_1_2_Certificado_ph import manejar_certificado_ph
            respuesta = await manejar_certificado_ph(numero)
            dataList.extend(respuesta)
            return dataList
        # Volver al menú de tipo de certificado (PU o PH)
        if estado == "certificado-pu-preguntas" and texto_real == "catastro-b":
            from app.services.handlers.catastro.B_1_Certificado_registro import manejar_certificado_registro
            respuesta = await manejar_certificado_registro(numero)
            dataList.extend(respuesta)
            return dataList
        # Volver al menú de tipo de certificado (PU o PH)
        if estado == "certificado-ph-preguntas" and texto_real == "catastro-b":
            from app.services.handlers.catastro.B_1_Certificado_registro import manejar_certificado_registro
            respuesta = await manejar_certificado_registro(numero)
            dataList.extend(respuesta)
            return dataList

        #PREGUNTAS de Certificado de registro A,B,C,D,E,F,G
        # Pregunta A: ¿Y si no tengo testimonio?
        if texto_real == "info-a":
            from app.services.handlers.catastro.B_1_1_info_1_A import manejar_info_certificado_pu_a
            respuesta = await manejar_info_certificado_pu_a(numero)
            dataList.extend(respuesta)
            return dataList
        # Pregunta B: ¿Dónde se realiza el trámite? (PU)
        if texto_real == "info-b":
            from app.services.handlers.catastro.B_1_1_info_1_B import manejar_info_certificado_pu_b
            respuesta = await manejar_info_certificado_pu_b(numero)
            dataList.extend(respuesta)
            return dataList
        # Pregunta C: ¿Qué es el certificado de registro catastral? (PU)
        if texto_real == "info-c":
            from app.services.handlers.catastro.B_1_1_info_1_C import manejar_info_certificado_pu_c
            respuesta = await manejar_info_certificado_pu_c(numero)
            dataList.extend(respuesta)
            return dataList
        # Pregunta D: ¿Para qué sirve el certificado? (PU)
        if texto_real == "info-d":
            from app.services.handlers.catastro.B_1_1_info_1_D import manejar_info_certificado_pu_d
            respuesta = await manejar_info_certificado_pu_d(numero)
            dataList.extend(respuesta)
            return dataList
        # Pregunta E: ¿Tiene un costo? (PU)
        if texto_real == "info-e":
            from app.services.handlers.catastro.B_1_1_info_1_E import manejar_info_certificado_pu_e
            respuesta = await manejar_info_certificado_pu_e(numero)
            dataList.extend(respuesta)
            return dataList
        # Pregunta F: ¿Qué obtengo al finalizar? (PU)
        if texto_real == "info-f":
            from app.services.handlers.catastro.B_1_1_info_1_F import manejar_info_certificado_pu_f
            respuesta = await manejar_info_certificado_pu_f(numero)
            dataList.extend(respuesta)
            return dataList
        # Pregunta G: ¿Quién puede hacerlo? (PU)
        if texto_real == "info-g":
            from app.services.handlers.catastro.B_1_1_info_1_G import manejar_info_certificado_pu_g
            respuesta = await manejar_info_certificado_pu_g(numero)
            dataList.extend(respuesta)
            return dataList

       

        #B_2_Duplicado de registro catastral
        # B_2_Duplicado_registro.py
        if texto_real == "req-catastro-2":
            from app.services.handlers.catastro.B_2_Duplicado_registro import manejar_certificado_duplicado
            respuesta = await manejar_certificado_duplicado(numero)
            dataList.extend(respuesta)
            return dataList
        # Volver desde duplicado de certificado al menú de requisitos generales
        if estado == "duplicado-certificado-preguntas" and texto_real == "catastro-b":
            from app.services.handlers.catastro.B_requisitos import manejar_requisitos_catastro
            await set_estado_usuario(numero, {"contexto": "catastro", "estado": "esperando-opcion"})
            respuesta = await manejar_requisitos_catastro(numero)
            dataList.extend(respuesta)
            return dataList

        # Duplicado_registro DR
        # Pregunta B: ¿Dónde se realiza este trámite? (Duplicado)
        if texto_real == "dr-info-b":
            from app.services.handlers.catastro.B_2_1_info_2_B import manejar_info_duplicado_b
            respuesta = await manejar_info_duplicado_b(numero)
            dataList.extend(respuesta)
            return dataList
        
        # Volver desde cualquier subvista del módulo duplicado-certificado
        if estado.startswith("duplicado-certificado-info-") and texto_real == "catastro-b":
            from app.services.handlers.catastro.B_2_Duplicado_registro import manejar_certificado_duplicado
            await set_estado_usuario(numero, {"contexto": "catastro", "estado": "duplicado-certificado-preguntas"})
            respuesta = await manejar_certificado_duplicado(numero)
            dataList.extend(respuesta)
            return dataList


        # Pregunta C: ¿Qué es un duplicado de certificado? (Duplicado)
        if texto_real == "dr-info-c":
            from app.services.handlers.catastro.B_2_2_info_2_C import manejar_info_duplicado_c
            respuesta = await manejar_info_duplicado_c(numero)
            dataList.extend(respuesta)
            return dataList
        
        
        # Pregunta D: ¿Para qué sirve el duplicado?
        if texto_real == "dr-info-d":
            from app.services.handlers.catastro.B_2_3_info_2_D import manejar_info_duplicado_d
            respuesta = await manejar_info_duplicado_d(numero)
            dataList.extend(respuesta)
            return dataList
        # Pregunta E: ¿Tiene un costo el duplicado?
        if texto_real == "dr-info-e":
            from app.services.handlers.catastro.B_2_4_info_2_E import manejar_info_duplicado_e
            respuesta = await manejar_info_duplicado_e(numero)
            dataList.extend(respuesta)
            return dataList
        # Pregunta F: ¿Qué obtengo con este trámite? (duplicado)
        if texto_real == "dr-info-f":
            from app.services.handlers.catastro.B_2_5_info_2_F import manejar_info_duplicado_f
            respuesta = await manejar_info_duplicado_f(numero)
            dataList.extend(respuesta)
            return dataList
        # Pregunta G: ¿Quién puede realizar este trámite? (duplicado)
        if texto_real == "dr-info-g":
            from app.services.handlers.catastro.B_2_5_info_2_G import manejar_info_duplicado_g
            respuesta = await manejar_info_duplicado_g(numero)
            dataList.extend(respuesta)
            return dataList

   
        #B_3_Actualizacion_catrastro
        if texto_real == "req-catastro-3":
            from app.services.handlers.catastro.B_3_Actualizacion_registro_cat import manejar_actualizacion_registro
            respuesta = await manejar_actualizacion_registro(numero)
            dataList.extend(respuesta)  # ✅ correcto
            return dataList
        
        if estado == "actualizacion-registro-preguntas" and texto_real == "catastro-b":
            # Volver al menú de requisitos generales
            await set_estado_usuario(numero, {"contexto": "catastro", "estado": "esperando-opcion"})
            from app.services.handlers.catastro.B_requisitos import manejar_requisitos_catastro
            respuesta = await manejar_requisitos_catastro(numero)
            dataList.extend(respuesta)
            return dataList

        # Volver desde cualquier subvista del módulo actualizacion-registro PREGUNTAS
        if estado.startswith("actualizacion-registro-info-") and texto_real == "catastro-b":
            from app.services.handlers.catastro.B_3_Actualizacion_registro_cat import manejar_actualizacion_registro
            await set_estado_usuario(numero, {"contexto": "catastro", "estado": "actualizacion-registro-preguntas"})
            respuesta = await manejar_actualizacion_registro(numero)
            dataList.extend(respuesta)
            return dataList

        # PREGUNTAS de Actualización de Registro B,C,D,E,F,G
        if texto_real == "ar-info-b":
            from app.services.handlers.catastro.B_3_1_info_3_B import manejar_info_actualizacion_b
            dataList.extend(await manejar_info_actualizacion_b(numero))
            return dataList

        if texto_real == "ar-info-c":
            from app.services.handlers.catastro.B_3_2_info_3_C import manejar_info_actualizacion_c
            respuesta = await manejar_info_actualizacion_c(numero)
            dataList.extend(respuesta)
            return dataList

        if texto_real == "ar-info-d":
            from app.services.handlers.catastro.B_3_3_info_3_D import manejar_info_actualizacion_d
            respuesta = await manejar_info_actualizacion_d(numero)
            dataList.extend(respuesta)
            return dataList

        if texto_real == "ar-info-e":
            from app.services.handlers.catastro.B_3_4_info_3_E import manejar_info_actualizacion_e
            respuesta = await manejar_info_actualizacion_e(numero)
            dataList.extend(respuesta)
            return dataList

        if texto_real == "ar-info-f":
            from app.services.handlers.catastro.B_3_5_info_3_F import manejar_info_actualizacion_f
            respuesta = await manejar_info_actualizacion_f(numero)
            dataList.extend(respuesta)
            return dataList

        if texto_real == "ar-info-g":
            from app.services.handlers.catastro.B_3_6_info_3_G import manejar_info_actualizacion_g
            respuesta = await manejar_info_actualizacion_g(numero)
            dataList.extend(respuesta)
            return dataList



        # B_4_Copias_legalizadas
        if texto_real == "req-catastro-4":
            from app.services.handlers.catastro.B_4_Copias_legalizadas import manejar_copias_legalizadas
            respuesta = await manejar_copias_legalizadas(numero)
            dataList.extend(respuesta)   
            return dataList              

        # Volver desde el submenú de Copias Legalizadas al menú de requisitos
        if estado == "copias-legalizadas-preguntas" and texto_real == "catastro-b":
            from app.services.handlers.catastro.B_requisitos import manejar_requisitos_catastro
            await set_estado_usuario(numero, {"contexto": "catastro", "estado": "esperando-opcion"})
            respuesta = await manejar_requisitos_catastro(numero)
            dataList.extend(respuesta)
            return dataList
        # Volver desde cualquier subvista del módulo copias-legalizadas (info-B, info-C, etc.)
        if estado.startswith("copias-legalizadas-info-") and texto_real == "catastro-b":
            from app.services.handlers.catastro.B_4_Copias_legalizadas import manejar_copias_legalizadas
            await set_estado_usuario(numero, {"contexto": "catastro", "estado": "copias-legalizadas-preguntas"})
            respuesta = await manejar_copias_legalizadas(numero)
            dataList.extend(respuesta)
            return dataList

        # PREGUNTAS de Copias Legalizadas B,C,D,E,F,G
        if texto_real == "rcl-info-b":
            from app.services.handlers.catastro.B_4_1_info_4_B import manejar_info_copias_legalizadas_b
            respuesta = await manejar_info_copias_legalizadas_b(numero)
            dataList.extend(respuesta)
            return dataList

        if texto_real == "rcl-info-c":
            from app.services.handlers.catastro.B_4_2_info_4_C import manejar_info_copias_legalizadas_c
            respuesta = await manejar_info_copias_legalizadas_c(numero)
            dataList.extend(respuesta)
            return dataList

        if texto_real == "rcl-info-d":
            from app.services.handlers.catastro.B_4_3_info_4_D import manejar_info_copias_legalizadas_d
            respuesta = await manejar_info_copias_legalizadas_d(numero)
            dataList.extend(respuesta)
            return dataList

        if texto_real == "rcl-info-e":
            from app.services.handlers.catastro.B_4_4_info_4_E import manejar_info_copias_legalizadas_e
            respuesta = await manejar_info_copias_legalizadas_e(numero)
            dataList.extend(respuesta)
            return dataList

        if texto_real == "rcl-info-f":
            from app.services.handlers.catastro.B_4_5_info_4_F import manejar_info_copias_legalizadas_f
            respuesta = await manejar_info_copias_legalizadas_f(numero)
            dataList.extend(respuesta)
            return dataList

        if texto_real == "rcl-info-g":
            from app.services.handlers.catastro.B_4_6_info_4_G import manejar_info_copias_legalizadas_g
            respuesta = await manejar_info_copias_legalizadas_g(numero)
            dataList.extend(respuesta)
            return dataList

        # B_5_Emisión de certificado Ley 247
        if texto_real == "req-catastro-5":
            from app.services.handlers.catastro.B_5_Emision_certificado_ley247 import manejar_emision_certificado_ley247
            return await manejar_emision_certificado_ley247(numero)
        
        # Volver desde submenú Ley 247 al menú de requisitos
        if estado == "emision-certificado-ley247-preguntas" and texto_real == "catastro-b":
            from app.services.handlers.catastro.B_requisitos import manejar_requisitos_catastro
            await set_estado_usuario(numero, {"contexto": "catastro", "estado": "esperando-opcion"})
            respuesta = await manejar_requisitos_catastro(numero)
            dataList.extend(respuesta)
            return dataList


        # Volver desde cualquier subvista del módulo Emisión de Certificado Ley 247
        if estado.startswith("emision-cert-ley247-info-") and texto_real == "cert-ley247-volver":
            from app.services.handlers.catastro.B_5_Emision_certificado_ley247 import manejar_emision_certificado_ley247
            await set_estado_usuario(numero, {
                "contexto": "catastro",
                "estado": "emision-certificado-ley247-preguntas"
            })
            respuesta = await manejar_emision_certificado_ley247(numero)
            dataList.extend(respuesta)
            return dataList

        # PREGUNTAS del trámite: Emisión de certificado catastral en el marco de la Ley 247 (B_5)
        if texto_real == "rec-info-b":
            from app.services.handlers.catastro.B_5_1_info_5_B import manejar_info_emision_cert_ley247_b
            respuesta = await manejar_info_emision_cert_ley247_b(numero)
            dataList.extend(respuesta)
            return dataList

        if texto_real == "rec-info-c":
            from app.services.handlers.catastro.B_5_2_info_5_C import manejar_info_emision_cert_ley247_c
            respuesta = await manejar_info_emision_cert_ley247_c(numero)
            dataList.extend(respuesta)
            return dataList

        if texto_real == "rec-info-d":
            from app.services.handlers.catastro.B_5_3_info_5_D import manejar_info_emision_cert_ley247_d
            respuesta = await manejar_info_emision_cert_ley247_d(numero)
            dataList.extend(respuesta)
            return dataList

        if texto_real == "rec-info-e":
            from app.services.handlers.catastro.B_5_4_info_5_E import manejar_info_emision_cert_ley247_e
            respuesta = await manejar_info_emision_cert_ley247_e(numero)
            dataList.extend(respuesta)
            return dataList

        if texto_real == "rec-info-f":
            from app.services.handlers.catastro.B_5_5_info_5_F import manejar_info_emision_cert_ley247_f
            respuesta = await manejar_info_emision_cert_ley247_f(numero)
            dataList.extend(respuesta)
            return dataList

        if texto_real == "rec-info-g":
            from app.services.handlers.catastro.B_5_6_info_5_G import manejar_info_emision_cert_ley247_g
            respuesta = await manejar_info_emision_cert_ley247_g(numero)
            dataList.extend(respuesta)
            return dataList

        
        
        # B_6_Reclamos y denuncias
        datalist = []

        if texto_real == "req-catastro-6":
            from app.services.handlers.catastro.B_6_Reclamos_denuncias import manejar_reclamos_denuncias
            respuesta = await manejar_reclamos_denuncias(numero)
            datalist.extend(respuesta)
            return datalist
        # Volver desde submenú de Reclamos y Denuncias al menú de requisitos
        if estado == "reclamos-denuncias" and texto_real == "catastro-b":
            from app.services.handlers.catastro.B_requisitos import manejar_requisitos_catastro
            await set_estado_usuario(numero, {"contexto": "catastro", "estado": "esperando-opcion"})
            respuesta = await manejar_requisitos_catastro(numero)
            dataList.extend(respuesta)
            return dataList

        # B_6_1_reclamo_catastro Reclamo: Quiero hacer un reclamo en temas catastrales
        if texto_real == "reclamo-catastro":
            from app.services.handlers.catastro.B_6_1_reclamo_catastro import manejar_reclamo_catastro
            respuesta = await manejar_reclamo_catastro(numero)
            datalist.extend(respuesta)
            return datalist
        # B_6_2_denuncia_construccion Denuncia: Dónde puedo denunciar la construcción de una casa
        if texto_real == "denuncia-construccion":
            from app.services.handlers.catastro.B_6_2_denuncia_construccion import manejar_denuncia_construccion
            respuesta = await manejar_denuncia_construccion(numero)
            datalist.extend(respuesta)
            return datalist
        # B_6_3_denuncia_avs
        if texto_real == "denuncia-avs":
            from app.services.handlers.catastro.B_6_3_denuncia_avs import manejar_denuncia_avs
            respuesta = await manejar_denuncia_avs(numero)
            datalist.extend(respuesta)
            return datalist
        # 🔄 Ver requisitos desde cualquier submenú (denuncias, reclamos, etc.)
        if texto_real == "catastro-b":
            from app.services.handlers.catastro.B_requisitos import manejar_requisitos_catastro
            await set_estado_usuario(numero, {"contexto": "catastro", "estado": "requisitos-catastro"})
            respuesta = await manejar_requisitos_catastro(numero)
            dataList.extend(respuesta)
            return dataList



        #INFO FICHAS CATASTRALES OPCION 1 (B)
        if texto_real == "info-fichas":
            from app.services.handlers.catastro.info_fichas_catastro import manejar_info_fichas
            respuesta = await manejar_info_fichas(numero)
            datalist = []  # ✅ Inicializamos aquí correctamente
            datalist.extend(respuesta)
            return datalist
        
        
        if estado == "fichas-catastro" and texto_real == "catastro-b":
            from app.services.handlers.catastro.B_1_Certificado_registro import manejar_certificado_registro
            respuesta = await manejar_certificado_registro(numero)
            dataList.extend(respuesta)
            return dataList

        # Volver al menú anterior desde info-fichas
        if estado == "fichas-catastro" and texto_real == "catastro-b":
            from app.services.handlers.catastro.B_1_Certificado_registro import manejar_certificado_registro
            respuesta = await manejar_certificado_registro(numero)
            dataList.extend(respuesta)
            return dataList
         # Volver al menú anterior desde info-fichas
        if estado == "leyes-catastro" and texto_real == "catastro-b":
            from app.services.handlers.catastro.B_1_Certificado_registro import manejar_certificado_registro
            respuesta = await manejar_certificado_registro(numero)
            dataList.extend(respuesta)
            return dataList
        if estado == "leyes-catastro" and texto_real == "catastro-b":
            from app.services.handlers.catastro.B_1_Certificado_registro import manejar_certificado_registro
            respuesta = await manejar_certificado_registro(numero)
            dataList.extend(respuesta)
            return dataList

       


        #INFO LEYES OPCION 2 (B)
        if texto_real == "info-leyes":
            from app.services.handlers.catastro.info_leyes_catastro import manejar_info_leyes
            respuesta = await manejar_info_leyes(numero)
            dataList.extend(respuesta)
            return dataList
        # Volver desde leyes-catastro
        if estado == "leyes-catastro" and texto_real == "inicio":
            from app.services.handlers.catastro.B_1_Certificado_registro import manejar_certificado_registro
            respuesta = await manejar_certificado_registro(numero)
            dataList.extend(respuesta)
            return dataList

        # Opción C → Puntos y horarios de atención
        if estado == "esperando-opcion" and texto_real == "catastro-c":
            from app.services.handlers.catastro.C_puntos_horarios_atencion import manejar_puntos_horarios
            respuesta = await manejar_puntos_horarios(numero)
            dataList.extend(respuesta)
            return dataList
        
        if texto_real == "volver-menu-catastro":
            from app.services.handlers.catastro.C_puntos_horarios_atencion import enviar_menu_catastro_principal
            payload = await enviar_menu_catastro_principal(numero)
            return [payload]

        # Volver desde Puntos y horarios (C) al menú de requisitos (catastro-b)
        if estado == "puntos-horarios" and texto_real == "catastro-b":
            from app.services.handlers.catastro.B_requisitos import manejar_requisitos_catastro
            await set_estado_usuario(numero, {"contexto": "catastro", "estado": "esperando-opcion"})
            respuesta = await manejar_requisitos_catastro(numero)
            dataList.extend(respuesta)
            return dataList
        # 🔄 Ver puntos y horarios desde cualquier submenú
        if texto_real == "catastro-c":
            from app.services.handlers.catastro.C_puntos_horarios_atencion import manejar_puntos_horarios
            await set_estado_usuario(numero, {
                "contexto": "catastro",
                "estado": "puntos-horarios"
            })
            respuesta = await manejar_puntos_horarios(numero)
            dataList.extend(respuesta)
            return dataList

        # Opción D → Preguntas frecuentes
        if texto_real == "catastro-d":
            from app.services.handlers.catastro.D_preguntas_frecuentes import manejar_preguntas_frecuentes
            respuesta = await manejar_preguntas_frecuentes(numero)
            datalist.extend(respuesta)
            return datalist
        
        # D_1_Pregunta frecuente: Información general sobre el catastro (1)
        if texto_real == "info-catastro-1":
            from app.services.handlers.catastro.D_1_info_catastro_1 import manejar_info_catastro_1
            respuesta = await manejar_info_catastro_1(numero)
            datalist.extend(respuesta)
            return datalist
        # D_1_1_info_catastro_1 → ¿Qué es el catastro municipal?
        if texto_real == "q-catastro-1":
            from app.services.handlers.catastro.D_1_1_info_catastro_1 import manejar_info_catastro_1_respuesta
            respuesta = await manejar_info_catastro_1_respuesta(numero)
            datalist.extend(respuesta)
            return datalist
        # D_1_2_info_catastro_1 → ¿Qué es un bien inmueble o predio?
        if texto_real == "q-catastro-2":
            from app.services.handlers.catastro.D_1_2_info_catastro_1 import manejar_info_catastro_2_respuesta
            respuesta = await manejar_info_catastro_2_respuesta(numero)
            datalist.extend(respuesta)
            return datalist
        # D_1_3_info_catastro_1 → ¿Qué es una ficha/formulario/etc. catastral?
        if texto_real == "q-catastro-3":
            from app.services.handlers.catastro.D_1_3_info_catastro_1 import manejar_info_catastro_3_respuesta
            respuesta = await manejar_info_catastro_3_respuesta(numero)
            datalist.extend(respuesta)
            return datalist
        # D_1_4_info_catastro_1 → ¿Qué es la georreferenciación en el catastro?
        if texto_real == "q-catastro-4":
            from app.services.handlers.catastro.D_1_4_info_catastro_1 import manejar_info_catastro_4_respuesta
            respuesta = await manejar_info_catastro_4_respuesta(numero)
            datalist.extend(respuesta)
            return datalist
        # D_1_5_info_catastro_1 → ¿Qué es el avalúo catastral?
        if texto_real == "q-catastro-5":
            from app.services.handlers.catastro.D_1_5_info_catastro_1 import manejar_info_catastro_5_respuesta
            respuesta = await manejar_info_catastro_5_respuesta(numero)
            datalist.extend(respuesta)
            return datalist
        # D_1_6_info_catastro_1 → ¿Qué es un conflicto de sobreposición catastral?
        if texto_real == "q-catastro-6":
            from app.services.handlers.catastro.D_1_6_info_catastro_1 import manejar_info_catastro_6_respuesta
            respuesta = await manejar_info_catastro_6_respuesta(numero)
            datalist.extend(respuesta)
            return datalist
        # D_1_7_info_catastro_1 → ¿Diferencia entre catastro urbano y rural?
        if texto_real == "q-catastro-7":
            from app.services.handlers.catastro.D_1_7_info_catastro_1 import manejar_info_catastro_7_respuesta
            respuesta = await manejar_info_catastro_7_respuesta(numero)
            datalist.extend(respuesta)
            return datalist
        # D_1_8_info_catastro_1 → ¿Qué son los bienes de dominio municipal?
        if texto_real == "q-catastro-8":
            from app.services.handlers.catastro.D_1_8_info_catastro_1 import manejar_info_catastro_8_respuesta
            respuesta = await manejar_info_catastro_8_respuesta(numero)
            datalist.extend(respuesta)
            return datalist
        # D_1_9_info_catastro_1 → ¿Beneficios de registrar un inmueble en catastro?
        if texto_real == "q-catastro-9":
            from app.services.handlers.catastro.D_1_9_info_catastro_1 import manejar_info_catastro_9_respuesta
            respuesta = await manejar_info_catastro_9_respuesta(numero)
            datalist.extend(respuesta)
            return datalist
        # D_1_10_info_catastro_1 → ¿Importancia del Certificado de Registro Catastral?
        if texto_real == "q-catastro-10":
            from app.services.handlers.catastro.D_1_10_info_catastro_1 import manejar_info_catastro_10_respuesta
            respuesta = await manejar_info_catastro_10_respuesta(numero)
            datalist.extend(respuesta)
            return datalist

        # Pregunta frecuente: Infraestructura y atención al ciudadano (2)
        if texto_real == "info-catastro-2":
            from app.services.handlers.catastro.D_2_info_catastro_2 import manejar_info_catastro_2
            respuesta = await manejar_info_catastro_2(numero)
            datalist.extend(respuesta)
            return datalist
        # D_2_1_info_catastro_2 → ¿Dónde se encuentra... y horario?
        if texto_real == "q-catastro-2-1":
            from app.services.handlers.catastro.D_2_1_info_catastro_2 import manejar_info_catastro_2_respuesta
            respuesta = await manejar_info_catastro_2_respuesta(numero)
            datalist.extend(respuesta)
            return datalist

        # (Opcional) D_2_2_info_catastro_2 → ¿Copias legalizadas en otra plataforma?
        if texto_real == "q-catastro-2-2":
            from app.services.handlers.catastro.D_2_2_info_catastro_2 import manejar_info_catastro_2_2_respuesta
            respuesta = await manejar_info_catastro_2_2_respuesta(numero)
            datalist.extend(respuesta)
            return datalist

        # Pregunta frecuente: Registro y documentación catastral (3)
        if texto_real == "info-catastro-3":
            from app.services.handlers.catastro.D_3_info_catastro_3 import manejar_info_catastro_3
            respuesta = await manejar_info_catastro_3(numero)
            datalist.extend(respuesta)
            return datalist
        if texto_real == "info-catastro-3-p2":
            from app.services.handlers.catastro.D_3_info_catastro_3_p2 import manejar_info_catastro_3_p2
            respuesta = await manejar_info_catastro_3_p2(numero)
            datalist.extend(respuesta)
            return datalist
        # D_3_1_info_catastro_3 → Tipos de bienes sujetos a registro catastral
        if texto_real == "q-catastro-3-1":
            from app.services.handlers.catastro.D_3_1_info_catastro_3 import manejar_info_catastro_3_1_respuesta
            respuesta = await manejar_info_catastro_3_1_respuesta(numero)
            datalist.extend(respuesta)
            return datalist
        # D_3_2_info_catastro_3 → ¿Qué es un levantamiento catastral?
        if texto_real == "q-catastro-3-2":
            from app.services.handlers.catastro.D_3_2_info_catastro_3 import manejar_info_catastro_3_2_respuesta
            respuesta = await manejar_info_catastro_3_2_respuesta(numero); datalist.extend(respuesta); return datalist

        # D_3_3_info_catastro_3 → ¿Qué es el código catastral…?
        if texto_real == "q-catastro-3-3":
            from app.services.handlers.catastro.D_3_3_info_catastro_3 import manejar_info_catastro_3_3_respuesta
            respuesta = await manejar_info_catastro_3_3_respuesta(numero); datalist.extend(respuesta); return datalist

        # D_3_4_info_catastro_3 → ¿Qué hago si pierdo mi código…?
        if texto_real == "q-catastro-3-4":
            from app.services.handlers.catastro.D_3_4_info_catastro_3 import manejar_info_catastro_3_4_respuesta
            respuesta = await manejar_info_catastro_3_4_respuesta(numero); datalist.extend(respuesta); return datalist

        # D_3_5_info_catastro_3 → ¿Qué es un certificado de no existencia…?
        if texto_real == "q-catastro-3-5":
            from app.services.handlers.catastro.D_3_5_info_catastro_3 import manejar_info_catastro_3_5_respuesta
            respuesta = await manejar_info_catastro_3_5_respuesta(numero); datalist.extend(respuesta); return datalist

        # D_3_6_info_catastro_3 → ¿Cómo solicitar un certificado de no existencia…?
        if texto_real == "q-catastro-3-6":
            from app.services.handlers.catastro.D_3_6_info_catastro_3 import manejar_info_catastro_3_6_respuesta
            respuesta = await manejar_info_catastro_3_6_respuesta(numero); datalist.extend(respuesta); return datalist

        # D_3_7_info_catastro_3 → ¿Cómo saber si está registrado como bien municipal?
        if texto_real == "q-catastro-3-7":
            from app.services.handlers.catastro.D_3_7_info_catastro_3 import manejar_info_catastro_3_7_respuesta
            respuesta = await manejar_info_catastro_3_7_respuesta(numero); datalist.extend(respuesta); return datalist

        # D_3_8_info_catastro_3 → ¿Qué documentos necesito…?
        if texto_real == "q-catastro-3-8":
            from app.services.handlers.catastro.D_3_8_info_catastro_3 import manejar_info_catastro_3_8_respuesta
            respuesta = await manejar_info_catastro_3_8_respuesta(numero); datalist.extend(respuesta); return datalist
        # D_3_9_info_catastro_3
        if texto_real == "q-catastro-3-9":
            from app.services.handlers.catastro.D_3_9_info_catastro_3 import manejar_info_catastro_3_9_respuesta
            respuesta = await manejar_info_catastro_3_9_respuesta(numero)
            datalist.extend(respuesta)
            return datalist

        # D_3_10_info_catastro_3
        if texto_real == "q-catastro-3-10":
            from app.services.handlers.catastro.D_3_10_info_catastro_3 import manejar_info_catastro_3_10_respuesta
            respuesta = await manejar_info_catastro_3_10_respuesta(numero)
            datalist.extend(respuesta)
            return datalist

        # D_3_11_info_catastro_3
        if texto_real == "q-catastro-3-11":
            from app.services.handlers.catastro.D_3_11_info_catastro_3 import manejar_info_catastro_3_11_respuesta
            respuesta = await manejar_info_catastro_3_11_respuesta(numero)
            datalist.extend(respuesta)
            return datalist

        # D_3_12_info_catastro_3
        if texto_real == "q-catastro-3-12":
            from app.services.handlers.catastro.D_3_12_info_catastro_3 import manejar_info_catastro_3_12_respuesta
            respuesta = await manejar_info_catastro_3_12_respuesta(numero)
            datalist.extend(respuesta)
            return datalist

        # Pregunta frecuente: Actualización y corrección de datos (4)
        if texto_real == "info-catastro-4":
            from app.services.handlers.catastro.D_4_info_catastro_4 import manejar_info_catastro_4
            respuesta = await manejar_info_catastro_4(numero)
            datalist.extend(respuesta)
            return datalist
        
        # D_4_1 → ¿Cómo se calcula el valor catastral...?
        if texto_real == "q-catastro-4-1":
            from app.services.handlers.catastro.D_4_1_info_catastro_4 import manejar_info_catastro_4_1_respuesta
            respuesta = await manejar_info_catastro_4_1_respuesta(numero); datalist.extend(respuesta); return datalist

        # D_4_2 → ¿Cómo afecta el uso del suelo...?
        if texto_real == "q-catastro-4-2":
            from app.services.handlers.catastro.D_4_2_info_catastro_4 import manejar_info_catastro_4_2_respuesta
            respuesta = await manejar_info_catastro_4_2_respuesta(numero); datalist.extend(respuesta); return datalist

        # D_4_3 → ¿Qué debo hacer si no está correctamente representado...?
        if texto_real == "q-catastro-4-3":
            from app.services.handlers.catastro.D_4_3_info_catastro_4 import manejar_info_catastro_4_3_respuesta
            respuesta = await manejar_info_catastro_4_3_respuesta(numero); datalist.extend(respuesta); return datalist
        # Pregunta frecuente: Herencias, copropiedades y terceros (5)
        if texto_real == "info-catastro-5":
            from app.services.handlers.catastro.D_5_info_catastro_5 import manejar_info_catastro_5
            respuesta = await manejar_info_catastro_5(numero)
            datalist.extend(respuesta)
            return datalist
        # D_5_1 → ¿Cómo obtener información de una vivienda que no es mi propiedad?
        if texto_real == "q-catastro-5-1":
            from app.services.handlers.catastro.D_5_1_info_catastro_5 import manejar_info_catastro_5_1_respuesta
            respuesta = await manejar_info_catastro_5_1_respuesta(numero); datalist.extend(respuesta); return datalist

        # D_5_2 → ¿Puedo realizar el trámite en nombre de una tercera persona?
        if texto_real == "q-catastro-5-2":
            from app.services.handlers.catastro.D_5_2_info_catastro_5 import manejar_info_catastro_5_2_respuesta
            respuesta = await manejar_info_catastro_5_2_respuesta(numero); datalist.extend(respuesta); return datalist

        # D_5_3 → ¿Si soy heredero del propietario original?
        if texto_real == "q-catastro-5-3":
            from app.services.handlers.catastro.D_5_3_info_catastro_5 import manejar_info_catastro_5_3_respuesta
            respuesta = await manejar_info_catastro_5_3_respuesta(numero); datalist.extend(respuesta); return datalist

        # D_5_4 → Contradicciones por divorcio
        if texto_real == "q-catastro-5-4":
            from app.services.handlers.catastro.D_5_4_info_catastro_5 import manejar_info_catastro_5_4_respuesta
            respuesta = await manejar_info_catastro_5_4_respuesta(numero); datalist.extend(respuesta); return datalist

        # D_5_5 → Copropietario sin presencia de los otros
        if texto_real == "q-catastro-5-5":
            from app.services.handlers.catastro.D_5_5_info_catastro_5 import manejar_info_catastro_5_5_respuesta
            respuesta = await manejar_info_catastro_5_5_respuesta(numero); datalist.extend(respuesta); return datalist

        # D_5_6 → Documentos si actúo como empresa
        if texto_real == "q-catastro-5-6":
            from app.services.handlers.catastro.D_5_6_info_catastro_5 import manejar_info_catastro_5_6_respuesta
            respuesta = await manejar_info_catastro_5_6_respuesta(numero); datalist.extend(respuesta); return datalist

        # Pregunta frecuente: Trámites y procedimientos (6)
        if texto_real == "info-catastro-6":
            from app.services.handlers.catastro.D_6_info_catastro_6 import manejar_info_catastro_6
            respuesta = await manejar_info_catastro_6(numero)
            datalist.extend(respuesta)
            return datalist
        
        # D_6_1 … D_6_7
        if texto_real == "q-catastro-6-1":
            from app.services.handlers.catastro.D_6_1_info_catastro_6 import manejar_info_catastro_6_1_respuesta
            respuesta = await manejar_info_catastro_6_1_respuesta(numero); datalist.extend(respuesta); return datalist
        if texto_real == "q-catastro-6-2":
            from app.services.handlers.catastro.D_6_2_info_catastro_6 import manejar_info_catastro_6_2_respuesta
            respuesta = await manejar_info_catastro_6_2_respuesta(numero); datalist.extend(respuesta); return datalist
        if texto_real == "q-catastro-6-3":
            from app.services.handlers.catastro.D_6_3_info_catastro_6 import manejar_info_catastro_6_3_respuesta
            respuesta = await manejar_info_catastro_6_3_respuesta(numero); datalist.extend(respuesta); return datalist
        if texto_real == "q-catastro-6-4":
            from app.services.handlers.catastro.D_6_4_info_catastro_6 import manejar_info_catastro_6_4_respuesta
            respuesta = await manejar_info_catastro_6_4_respuesta(numero); datalist.extend(respuesta); return datalist
        if texto_real == "q-catastro-6-5":
            from app.services.handlers.catastro.D_6_5_info_catastro_6 import manejar_info_catastro_6_5_respuesta
            respuesta = await manejar_info_catastro_6_5_respuesta(numero); datalist.extend(respuesta); return datalist
        if texto_real == "q-catastro-6-6":
            from app.services.handlers.catastro.D_6_6_info_catastro_6 import manejar_info_catastro_6_6_respuesta
            respuesta = await manejar_info_catastro_6_6_respuesta(numero); datalist.extend(respuesta); return datalist
        if texto_real == "q-catastro-6-7":
            from app.services.handlers.catastro.D_6_7_info_catastro_6 import manejar_info_catastro_6_7_respuesta
            respuesta = await manejar_info_catastro_6_7_respuesta(numero); datalist.extend(respuesta); return datalist
        # Pregunta frecuente: Requisitos y permisos (7)
        if texto_real == "info-catastro-7":
            from app.services.handlers.catastro.D_7_info_catastro_7 import manejar_info_catastro_7
            respuesta = await manejar_info_catastro_7(numero)
            datalist.extend(respuesta)
            return datalist
        # D_7_1 → ¿Se necesita permiso para hacer un cuarto fuera de mi casa?
        if texto_real == "q-catastro-7-1":
            from app.services.handlers.catastro.D_7_1_info_catastro_7 import manejar_info_catastro_7_1_respuesta
            respuesta = await manejar_info_catastro_7_1_respuesta(numero); datalist.extend(respuesta); return datalist

        # D_7_2 → ¿Qué documentos necesito para solicitar copias simples o legalizadas…?
        if texto_real == "q-catastro-7-2":
            from app.services.handlers.catastro.D_7_2_info_catastro_7 import manejar_info_catastro_7_2_respuesta
            respuesta = await manejar_info_catastro_7_2_respuesta(numero); datalist.extend(respuesta); return datalist

        # Opción E → Contactos y direcciones
        if estado == "esperando-opcion" and texto_real == "catastro-e":
            from app.services.handlers.catastro.E_contactos_direcciones import manejar_contactos_direcciones
            respuesta = await manejar_contactos_direcciones(numero)
            dataList.extend(respuesta)
            return dataList

        # E_1_Cuando el usuario selecciona una opción desde la lista
        if estado == "contactos-direcciones":
            if texto_real == "audiencia-acm":
                from app.services.handlers.catastro.E_1_solicitar_audiencia_autoridad import manejar_solicitud_audiencia_acm
                respuesta = await manejar_solicitud_audiencia_acm(numero)
                dataList.extend(respuesta)
                return dataList

            if texto_real == "atras":
                return await self.handle_message("", numero, name, msg_id)
        # E_1_1 → Submenú dentro de audiencia-acm
        if estado == "audiencia-acm":
            if texto_real == "descargar-nota":
                texto = "📥 *Descargar nota modelo:*\nhttp://35.232.232.3:4002/NOTA_DE_SOLICITUD_DE_AUDIENCIA.docx"
                dataList.append(await crear_payload_texto(numero, texto))
               
                return dataList

            if texto_real == "entregar-nota":
                texto = (
                    "📬 *¿Dónde entregarla?*\n\n"
                    "Puedes solicitarla mediante correspondencia ciudadana, con una nota simple ingresada por ventanilla de SITRAM "
                    "(calle Potosí, edificio Tobia, planta baja).\n"
                    "🕘 De lunes a viernes, de 8:45 am a 16:10 pm."
                )
                dataList.append(await crear_payload_texto(numero, texto))
               
                return dataList

            if texto_real == "atras":
                return await self.handle_message("catastro-e", numero, name, msg_id)
            



        return dataList

    def _payload_custom_menu(self, numero: str, mensaje: str) -> dict:
        seccion = self.msg_handler.build_seccion("🚀 Servicios Disponibles")
        secciones = [seccion]
        btn_lbl = "Ver servicios"
        return payload_interactivo_lista(numero, mensaje, secciones, btn_lbl)

    def _extraer_texto_id(self, texto: Any) -> str:
        """
        Extrae el id real cuando el mensaje es interactivo (lista).
        """
        if isinstance(texto, dict) and texto.get("type") == "interactive":
            interactive = texto.get("interactive", {})
            if interactive.get("type") == "list_reply":
                return interactive["list_reply"]["id"]
        return str(texto)

#





