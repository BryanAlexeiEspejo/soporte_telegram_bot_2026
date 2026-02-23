import requests
import os
import re
import json
from typing import List, Dict, Any, Optional
from rapidfuzz import process
from dotenv import load_dotenv

from app.database.database import set_estado_usuario, get_estado_usuario, registrar_historial
from app.services.utils.utils_handler import payload_interactivo_lista
from app.services.openAI.ctx_analitycs import consultar_contexto_ia
from app.services.handlers.atm_ia_handler import ATMInteligenciaHandler

from app.services.handlers.hospitales_handler import HospitalesHandler
from app.services.handlers.ciudadano_handler import CiudadanoHandler
from app.services.handlers.catastro_handler import CatastroHandler
from app.services.handlers.tramites_handler import TramitesHandler
from app.services.handlers.peludos_handler import PeludosHandler
from app.services.handlers.cjueves_handler import CjuevesHandler
from app.services.handlers.igob_handler import IgobHandler
from app.services.handlers.catm_handler import CatmHandler
from app.services.handlers.chatbot_handler import ChatbotHandler
from app.services.handlers.soporte_handler import SoporteHandler  # <-- nuevo
from app.services.feedback.feedback_service import (
    build_useful_prompt, build_rating_prompt, thanks_text, ask_free_question,
    start_feedback_record, set_useful, set_rating, set_feedback_question
)

# Importar servicios de Telegram (solo para generar keyboards si necesitamos)
from app.services.telegram_service import telegram_service

load_dotenv()

class MessageHandler:
    """Dispatcher principal con arquitectura de handlers y contexto"""

    def __init__(self):
        self._last_msg_id_by_user: Dict[str, str] = {}
        self.platform = "whatsapp"  # Plataforma por defecto

        # Handlers registrados (incluir 'soporte' pero NO mostrar el resto en el menú)
        self.handlers = {
            "igob":      {"handler": IgobHandler(self),      "title": "Recupera contraseña IGOB", "desc": "🔐Recupera tu clave al instante sin filas ni esperas."},
            "atm":       {"handler": CatmHandler(self),      "title": "Admin. Tributaria - ATM", "desc": "🏛️ Impuestos municipales, alivio tributario."},
            "tramites":  {"handler": TramitesHandler(self),  "title": "Seguimiento de trámites",  "desc": "📄Consulta el estado de licencias, permisos y otros trámites."},
            "catastro":  {"handler": CatastroHandler(self),  "title": "Información catastral",    "desc": "❕Consulta el estado de tu trámite catastral."},
            "ciudadano": {"handler": CiudadanoHandler(self), "title": "Información ciudadana",    "desc": "💳Puntos horarios de atención municipal, requisitos incluidos"},
            "limpieza":  {"handler": CjuevesHandler(self),   "title": "100 jueves de acción",     "desc": "🌿Solicita limpieza y mejoras para tu barrio"},
            "chatbot":   {"handler": ChatbotHandler(self),  "title": "Calificar Chatbot",        "desc": "⭐ Dale una calificación al servicio del chatbot"},
            "soporte":   {"handler": SoporteHandler(self),  "title": "Soporte Técnico",          "desc": "🛠️ Consulta y seguimiento de tickets — Entrega y Recojo de Equipos"},
        }

        # Handler IA (registrado pero no mostrado en el menú por defecto)
        self._atm_ia_keyword = os.getenv("ATM_IA_KEYWORD", "prueba atm inteligencia").strip().lower()
        self.handlers["atm_ia"] = {
            "handler": ATMInteligenciaHandler(self),
            "title": "ATM IA - Asistente oficial",
            "desc": "💬 Chat en lenguaje natural con información oficial de la ATM"
        }

        self.feedback_states = {
            'WAITING_USEFUL': 'waiting_useful',
            'WAITING_RATING': 'waiting_rating',
            'WAITING_FEEDBACK_QUESTION': 'waiting_feedback_question'
        }

        self._atm_keywords = {"atm", "alivio", "alivio tributario", "impuesto", "impuestos", "tributario"}

        # emoji regex amplio (incluye ZWJ y VS16)
        self._emoji_re = re.compile(
            "[" 
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F1E0-\U0001F1FF"
            u"\U0001F900-\U0001F9FF"
            u"\U0001FA70-\U0001FAFF"
            u"\u2600-\u26FF"
            u"\u2700-\u27BF"
            u"\u200d"
            u"\ufe0f"
            "]+",
            flags=re.UNICODE
        )

        # Comandos de saludo / salida globales (minúsculas)
        self._greetings = {"hola", "buenos dias", "buenos días", "buenas tardes", "buenas noches", "buen dia", "buen día", "inicio", "/start", "start"}
        self._exit_words = {"salir", "/salir", "exit"}
        
    # async def force_remove_keyboard(chat_id: str):
    #     await telegram_service.send_message(
    #         chat_id=chat_id,
    #         text="‎",  # caracter invisible
    #         reply_markup={"remove_keyboard": True}
    #     )

    # ------------------ UTIL HELPERS ------------------
    def _force_extract_raw_text(self, msg: Any) -> str:
        try:
            if isinstance(msg, dict):
                if msg.get("type") == "text" and isinstance(msg.get("text"), dict):
                    return str(msg["text"].get("body", "") or "")
                if msg.get("type") == "interactive":
                    inter = msg.get("interactive", {})
                    if "button_reply" in inter and isinstance(inter["button_reply"], dict):
                        return str(inter["button_reply"].get("title", "") or inter["button_reply"].get("id", ""))
                    if "list_reply" in inter and isinstance(inter["list_reply"], dict):
                        return str(inter["list_reply"].get("title", "") or inter["list_reply"].get("id", ""))
                if msg.get("type") == "sticker":
                    return ""
                if "text" in msg and isinstance(msg["text"], dict) and msg["text"].get("body"):
                    return str(msg["text"].get("body") or "")
                if "body" in msg:
                    return str(msg.get("body") or "")
                if "message" in msg and isinstance(msg["message"], dict):
                    nested = msg["message"]
                    if "text" in nested and isinstance(nested["text"], dict):
                        return str(nested["text"].get("body") or "")
                    if "body" in nested:
                        return str(nested.get("body") or "")
                return str(msg)
            else:
                return str(msg or "")
        except Exception:
            return str(msg or "")

    def _extract_interactive_id(self, texto: Any) -> str:
        try:
            if isinstance(texto, dict) and texto.get("type") == "interactive":
                inter = texto.get("interactive", {})
                if inter.get("type") == "list_reply":
                    return (inter.get("list_reply", {}).get("id", "") or "").strip().lower()
                elif inter.get("type") == "button_reply":
                    return (inter.get("button_reply", {}).get("id", "") or "").strip().lower()
            raw = self._force_extract_raw_text(texto)
            return raw.strip().lower()
        except Exception:
            return str(texto).strip().lower()

    # ------------------ MAIN ENTRY ------------------
    async def process_message(self, texto: Any, numero: str, name: str, 
                             msg_id: str = "", consumer_id: int = 0,
                             platform: str = "whatsapp") -> List[Dict[str, Any]]:
        """
        Punto de entrada principal.
        Devuelve una lista de payloads estilo WhatsApp (o simples text payloads).
        Cuando platform == "telegram" el controlador adaptará estos payloads a Telegram.
        """
        self.platform = platform
        
        user_state = await get_estado_usuario(numero)
        contexto = user_state.get("contexto", "") if user_state else ""
        estado = user_state.get("estado", "") if user_state else ""
        feedback_id = user_state.get("feedback_id", "") if user_state else ""

        # Dedupe salvo feedback
        if estado not in [
            self.feedback_states['WAITING_USEFUL'],
            self.feedback_states['WAITING_RATING'],
            self.feedback_states['WAITING_FEEDBACK_QUESTION']
        ]:
            if msg_id:
                if self._last_msg_id_by_user.get(numero) == msg_id:
                    return []
                self._last_msg_id_by_user[numero] = msg_id

        # Normalizador / id interactivo
        def _id_interactivo(msg: Any) -> str:
            if isinstance(msg, dict) and msg.get("type") == "interactive":
                inter = msg.get("interactive", {})
                t = inter.get("type")
                if t == "list_reply":
                    return (inter.get("list_reply", {}).get("id") or "").strip().lower()
                if t == "button_reply":
                    return (inter.get("button_reply", {}).get("id") or "").strip().lower()
            return self._force_extract_raw_text(msg).strip().lower()

        texto_id = _id_interactivo(texto)
        texto_preview = self._force_extract_raw_text(texto)[:120]

        # Registrar historial USUARIO (usar preview para evitar excepciones)
        try:
            await registrar_historial(
                origen="TELEGRAM_USER" if platform == "telegram" else "USUARIO",
                actor=name,
                numero=numero,
                texto=texto_preview
            )
        except Exception:
            pass

        print(f"🔍 DEBUG: texto_id='{texto_id}', numero={numero}, name={name}, platform={platform}")
        print(f"🔍 DEBUG: contexto='{contexto}', estado='{estado}', feedback_id='{feedback_id}', preview='{texto_preview}'")

        # Si el texto es vacío o muy corto, mostrar menú principal
        if not texto_id or texto_id in {".", "..."}:
            return await self._show_main_menu(numero, name, show_not_understood=True)

        # Manejar flujo de feedback si está activo (primero)
        if estado in [self.feedback_states['WAITING_USEFUL'],
                      self.feedback_states['WAITING_RATING'],
                      self.feedback_states['WAITING_FEEDBACK_QUESTION']]:
            return await self._handle_feedback_flow(texto, numero, name, msg_id, user_state)

        respuestas_despedida = {
            "adiós": "¡Hasta pronto! Espero verte de nuevo pronto 😊.",
            "chao": "¡Chao! Nos vemos pronto 👋.",
            "hasta luego": "Hasta luego, ¡vuelve pronto! 😄.",
            "muchas gracias": "¡De nada! Siempre estoy aquí para ayudarte 😊.",
            "gracias": "¡De nada! 😊 estoy aquí para ayudarte.",
        }

        print("📡", name, "(", numero, ") dice:", texto, " - ", msg_id, " - Plataforma:", platform)

        # ------------------ Si ya estamos EN atm_ia -> permanecer allí ------------------
        if contexto == "atm_ia":
            if texto_id in self._greetings or texto_id in self._exit_words:
                try:
                    await set_estado_usuario(numero, {"contexto": "", "estado": "", "ci": "", "mail": "", "feedback_id": ""})
                except Exception:
                    pass
                return await self._show_main_menu(numero, name)

            atm_handler = self.handlers.get("atm_ia", {}).get("handler")
            if atm_handler:
                try:
                    return await atm_handler.handle_message(texto, numero, name, msg_id)
                except Exception:
                    try:
                        await set_estado_usuario(numero, {"contexto": "atm_ia", "estado": "conversando-ia"})
                    except Exception:
                        pass
                    return [{
                        "messaging_product": "whatsapp",
                        "to": numero,
                        "type": "text",
                        "text": {"body": "❌ Ocurrió un error procesando tu consulta. Intenta nuevamente o escribe SALIR para volver al menú."}
                    }]

        # ---------- Prioridad: keyword atm_ia ----------
        try:
            if estado not in [self.feedback_states['WAITING_USEFUL'],
                              self.feedback_states['WAITING_RATING'],
                              self.feedback_states['WAITING_FEEDBACK_QUESTION']]:
                if self._atm_ia_keyword and texto_id == self._atm_ia_keyword:
                    await set_estado_usuario(numero, {
                        "contexto": "atm_ia",
                        "estado": "conversando-ia",
                        "ci": "",
                        "mail": "",
                        "feedback_id": ""
                    })
                    return await self.handlers["atm_ia"]["handler"].handle_message(texto, numero, name, msg_id)
        except Exception:
            pass

        # Si usuario selecciona opción del menú principal (interactive list ids)
        if texto_id in self.handlers:
            handler_entry = self.handlers.get(texto_id)
            if handler_entry and handler_entry.get("handler"):
                await set_estado_usuario(numero, {"contexto": texto_id, "estado": "", "ci": "", "mail": "", "feedback_id": ""})
                return await handler_entry["handler"].handle_message(texto, numero, name, msg_id)

        # Saludo / reset fuzzy
        comandos_iniciales = ["hola", "buenos dias", "buenos días", "buenas tardes", "buenas noches", "buen dia", "buen día", "que onda", "inicio", "/start", "start"]
        mejor_match, puntaje, _ = process.extractOne(texto_id, comandos_iniciales)
        if puntaje > 60 and abs(len(texto_id) - len(mejor_match)) <= 3:
            await set_estado_usuario(numero, {"contexto": "", "estado": "", "ci": "", "mail": "", "feedback_id": ""})
            return await self._show_main_menu(numero, name)

        # Atajo a ATM sin romper subcomandos
        if texto_id.startswith("atm-") or texto_id.startswith("q-atm-"):
            return await self.handlers["atm"]["handler"].handle_message(texto, numero, name, msg_id)
        if texto_id in self._atm_keywords:
            await set_estado_usuario(numero, {"contexto": "atm", "estado": "esperando-opcion", "ci": "", "mail": "", "feedback_id": ""})
            return await self.handlers["atm"]["handler"].handle_message(texto, numero, name, msg_id)

        # Intent detection: si no hay contexto, intentar inferir (fallback)
        if not contexto:
            try:
                contexto = await consultar_contexto_ia(str(texto or "")) or ""
            except Exception:
                contexto = ""

        # Si hay contexto vigente, delega
        if contexto and contexto in self.handlers:
            handler = self.handlers[contexto]["handler"]
            return await handler.handle_message(texto, numero, name, msg_id)

        # Descubrir intención con can_handle
        for handler_name, handler_info in self.handlers.items():
            handler = handler_info["handler"]
            try:
                if handler and hasattr(handler, 'can_handle') and await handler.can_handle(texto_id, numero, user_state or {}):
                    await set_estado_usuario(numero, {"contexto": handler_name, "estado": "", "ci": "", "mail": "", "feedback_id": ""})
                    return await handler.handle_message(texto, numero, name, msg_id)
            except Exception as e:
                print(f"⚠️ can_handle error en {handler_name}:", e)

        # Despedidas fuzzy
        mejor_match, puntaje, _ = process.extractOne(texto_id, list(respuestas_despedida.keys()))
        if puntaje > 60 and abs(len(texto_id) - len(mejor_match)) <= 3:
            mensaje = respuestas_despedida[mejor_match]
            seccion = self.build_seccion("🚀 Servicios Disponibles")
            payload = payload_interactivo_lista(numero, f"{mensaje}\n\nGracias por tu tiempo 🙌. Si aún quieres, puedes revisar nuestros servicios 👇", [seccion], "Ver servicios")
            return [payload]

        # Si no se entendió, mostrar menú principal con mensaje de no entendido
        return await self._show_main_menu(numero, name, show_not_understood=True)

    # ------------------ FEEDBACK FLOW ------------------
    async def _handle_feedback_flow(self, texto: Any, numero: str, name: str, msg_id: str, user_state: dict) -> List[Dict[str, Any]]:
        estado = user_state.get("estado", "")
        feedback_id = user_state.get("feedback_id", "")

        texto_str = self._force_extract_raw_text(texto)
        texto_limpio = texto_str.strip()
        texto_id = self._extract_interactive_id(texto)
        texto_id_lower = (texto_id or "").strip().lower()

        print(f"🔍 DEBUG _handle_feedback_flow: estado='{estado}', feedback_id='{feedback_id}', texto_raw='{texto_str}', texto_id='{texto_id}'")

        contains_emoji = bool(self._emoji_re.search(texto_str or ""))

        if estado == self.feedback_states['WAITING_USEFUL']:
            respuesta_si = texto_id_lower in ["fb_yes", "si", "sí", "yes", "útil", "util"]
            respuesta_no = texto_id_lower in ["fb_no", "no", "nope", "no útil", "no util"]
            if respuesta_si:
                set_useful(feedback_id, True)
                await set_estado_usuario(numero, {
                    "contexto": "feedback",
                    "estado": self.feedback_states['WAITING_RATING'],
                    "feedback_id": feedback_id
                })
                return [build_rating_prompt(numero)]
            if respuesta_no:
                set_useful(feedback_id, False)
                await set_estado_usuario(numero, {
                    "contexto": "feedback",
                    "estado": self.feedback_states['WAITING_FEEDBACK_QUESTION'],
                    "feedback_id": feedback_id
                })
                return [ask_free_question(numero)]
            return [build_useful_prompt(numero)]

        if estado == self.feedback_states['WAITING_RATING']:
            rating = None
            if isinstance(texto_id, str) and texto_id.startswith("fb_rating_"):
                try:
                    rating = int(texto_id.split("_")[2])
                except Exception:
                    rating = None
            if rating is None:
                m = re.search(r'[1-5]', texto_str or "")
                if m:
                    try:
                        rating = int(m.group())
                    except:
                        rating = None
            if rating and 1 <= rating <= 5:
                set_rating(feedback_id, rating)
                await set_estado_usuario(numero, {"contexto": "", "estado": "", "feedback_id": "", "ci": "", "mail": ""})
                return [thanks_text(numero, "✨ ¡Gracias por tu calificación! ¿En qué más puedo ayudarte?")]
            return [build_rating_prompt(numero)]

        if estado == self.feedback_states['WAITING_FEEDBACK_QUESTION']:
            comandos_salir = set(list(self.handlers.keys()) + ["inicio", "hola", "menu", "salir", "cancelar", "servicios", "ver servicios"])
            if texto_id_lower in comandos_salir or texto_limpio.lower() in comandos_salir:
                return [{
                    "messaging_product": "whatsapp",
                    "to": numero,
                    "type": "text",
                    "text": {
                        "body": "🙏 Para continuar con otros servicios, por favor completa primero esta breve encuesta. Tu opinión es necesaria para mejorar."
                    }
                }]

            if contains_emoji:
                return [{
                    "messaging_product": "whatsapp",
                    "to": numero,
                    "type": "text",
                    "text": {
                        "body": "😅 Necesito un comentario más descriptivo sin emojis. Por favor escribe una breve explicación (mínimo 3 letras) sin emojis. 🙏"
                    }
                }]

            letters_only = "".join(ch for ch in texto_limpio if ch.isalpha())
            letters_count = sum(1 for ch in letters_only if ch.isalpha())

            if letters_count < 3:
                return [{
                    "messaging_product": "whatsapp",
                    "to": numero,
                    "type": "text",
                    "text": {
                        "body": "📄 El comentario es muy corto o no aporta información útil. Por favor escribe al menos *3 letras* (sin emojis). 🙏"
                    }
                }]

            unique_chars = set(ch.lower() for ch in letters_only)
            if len(unique_chars) <= 1:
                return [{
                    "messaging_product": "whatsapp",
                    "to": numero,
                    "type": "text",
                    "text": {
                        "body": "🔎 Necesito un comentario más descriptivo (no repitas la misma letra). Por favor escribe una breve explicación sin emojis. 🙏"
                    }
                }]

            try:
                set_feedback_question(feedback_id, texto_str)
            except Exception:
                return [{
                    "messaging_product": "whatsapp",
                    "to": numero,
                    "type": "text",
                    "text": {
                        "body": "❌ Hubo un error guardando tu comentario. Por favor inténtalo de nuevo."
                    }
                }]

            await set_estado_usuario(numero, {"contexto": "", "estado": "", "feedback_id": "", "ci": "", "mail": ""})
            return [thanks_text(numero, "✨ ¡Gracias por tus comentarios! Los revisaremos para mejorar. 🙌")]

        await set_estado_usuario(numero, {"contexto": "", "estado": "", "feedback_id": "", "ci": "", "mail": ""})
        return await self._show_main_menu(numero, name)

    # ------------------ START FEEDBACK ------------------
    async def start_feedback_after_response(
        self,
        numero: str,
        name: str,
        question: str,
        answer: str,
        conversation_id: str = None,
        flow: str = "chatbot",
        flow_id: str = None
    ) -> List[Dict[str, Any]]:
        try:
            feedback_id = start_feedback_record(
                user_id=numero,
                user_name=name,
                question=question,
                answer=answer,
                conversation_id=conversation_id,
                flow=flow,
                flow_id=flow_id
            )
            await set_estado_usuario(numero, {
                "contexto": "feedback",
                "estado": self.feedback_states['WAITING_USEFUL'],
                "feedback_id": feedback_id,
                "ci": "",
                "mail": ""
            })
            return [build_useful_prompt(numero)]
        except Exception as e:
            print(f"❌ Error al iniciar feedback: {e}")
            import traceback
            traceback.print_exc()
            return []

    # ------------------ UI / HELPERS ------------------
    async def _show_main_menu(self, numero: str, name: str, show_not_understood: bool = False) -> List[Dict[str, Any]]:
        """
        Construye y devuelve el menú principal en formato payload_interactivo_lista (estilo WhatsApp).
        Ahora el menú contiene SOLO la opción 'soporte' con su descripción.
        """
        mensaje_comp = "Creo que no te entendí bien 🤔, vamos a intentarlo una vez más.\n" if show_not_understood else ""
        bot_name = os.getenv("BOT_NAME", "AMI")
        # Mensaje centrado en SOPORTE (solicitud pedida por ti)
        mensaje = (
            f"¡Hola! {name} 👋.\n"
            f"{mensaje_comp}"
            "A continuación encontrarás la opción de Soporte Técnico para consultar y hacer seguimiento de tus tickets.\n\n"
            "Soporte Técnico — Consulta el estado, historial y seguimiento de solicitudes (Entrega y Recojo de Equipos)."
        )
        seccion = self.build_seccion("🛠️ Soporte Técnico")
        payload = payload_interactivo_lista(numero, mensaje, [seccion], "Abrir Soporte")
        return [payload]

    def build_seccion(self, titulo_seccion) -> Dict[str, Any]:
        """
        Construye la sección para el payload interactivo.
        MODIFICADO: el menú mostrará únicamente la opción 'soporte'.
        """
        def _truncate(s: str, n: int) -> str:
            s = (s or "")
            if len(s) <= n:
                return s
            return s[: n - 3].rstrip() + "..."

        seccion = {"title": titulo_seccion, "rows": []}

        # Agregar SOLO la opción 'soporte' al menú principal
        info = self.handlers.get("soporte")
        if info:
            seccion["rows"].append({
                "id": "soporte",
                "title": _truncate(info.get("title", "Soporte Técnico"), 24),
                "description": _truncate(info.get("desc", "Consulta y seguimiento de tickets"), 72),
            })

        return seccion

    # ------------------ ADAPTACIÓN PARA TELEGRAM ------------------
    async def adapt_responses_for_telegram(self, responses: List[Dict]) -> List[Dict]:
        """
        Adapta una lista de respuestas (estilo WhatsApp/internal) a formato Telegram.
        Devuelve lista de dicts listos para pasarse a telegram_service.send_message.
        """
        if not responses or self.platform != "telegram":
            return responses or []

        telegram_responses = []
        for response in responses:
            telegram_response = await self.convert_to_telegram_format(response)
            if telegram_response:
                telegram_responses.append(telegram_response)

        return telegram_responses

    async def convert_to_telegram_format(self, response: Dict) -> Optional[Dict]:
        """Convierte una respuesta de WhatsApp a Telegram"""
        try:
            # Si la respuesta ya es para Telegram (tiene chat_id), la devolvemos tal cual
            if "chat_id" in response:
                return response

            # Si es una respuesta de WhatsApp, la convertimos
            msg_type = response.get("type", "")

            # obtener chat_id ("to" en el payload whatsapp/internal)
            to_field = response.get("to") or response.get("recipient") or response.get("numero") or response.get("chat_id")
            try:
                chat_id = int(to_field)
            except Exception:
                # No se puede convertir; ignorar
                return None

            if msg_type == "text":
                text = response.get("text", {}).get("body", "")
                # Convertir formato WhatsApp a HTML para Telegram
                # Reemplazos simples: *bold* -> <b>bold</b>, _italic_ -> <i>italic</i>
                # Nota: hacer reemplazos simples, en tu flujo puedes mejorar escapes si necesitas MarkdownV2
                text = text.replace("*", "<b>").replace("*", "</b>")
                text = text.replace("_", "<i>").replace("_", "</i>")
                text = text.replace("~", "<s>").replace("~", "</s>")
                text = text.replace("```", "<code>").replace("```", "</code>")

                return {
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "HTML"
                }

            elif msg_type == "interactive":
                interactive = response.get("interactive", {})
                inter_type = interactive.get("type", "")

                if inter_type == "button":
                    body = interactive.get("body", {}).get("text", "")
                    buttons = interactive.get("action", {}).get("buttons", [])

                    # Convertir botones a formato Telegram
                    telegram_buttons = []
                    for button in buttons:
                        if button.get("type") == "reply":
                            reply = button.get("reply", {})
                            telegram_buttons.append([{
                                "text": reply.get("title", ""),
                                "callback_data": reply.get("id", "")
                            }])

                    keyboard = telegram_service.create_inline_keyboard(telegram_buttons)

                    return {
                        "chat_id": chat_id,
                        "text": body,
                        "parse_mode": "HTML",
                        "reply_markup": keyboard
                    }

                elif inter_type == "list":
                    body = interactive.get("body", {}).get("text", "")
                    sections = interactive.get("action", {}).get("sections", [])

                    # Convertir lista a botones de Telegram
                    telegram_buttons = []
                    for section in sections:
                        rows = section.get("rows", [])
                        for row in rows:
                            telegram_buttons.append([{
                                "text": row.get("title", ""),
                                "callback_data": row.get("id", "")
                            }])

                    keyboard = telegram_service.create_inline_keyboard(telegram_buttons)

                    return {
                        "chat_id": chat_id,
                        "text": body,
                        "parse_mode": "HTML",
                        "reply_markup": keyboard
                    }

            # Si no se puede convertir, devolver texto plano
            return {
                "chat_id": chat_id,
                "text": "📨 Mensaje recibido",
                "parse_mode": "HTML"
            }

        except Exception:
            print("❌ Error convirtiendo a Telegram")
            return None

    # ------------------ ENVÍO DE MENSAJES (helpers usados para WhatsApp) ------------------
    async def send_messages(self, dataList: List[Dict[str, Any]]) -> None:
        """Envía mensajes según la plataforma (método legacy)."""
        if self.platform == "telegram":
            await self.send_telegram_messages(dataList)
        else:
            await self.send_whatsapp_messages(dataList)

    async def send_telegram_messages(self, dataList: List[Dict]) -> None:
        """Envia mensajes a Telegram usando telegram_service.
        Hotfix: convierte cualquier ReplyKeyboard (keyboard) en InlineKeyboard para evitar teclados persistentes.
        """
        import re
        for data in dataList:
            try:
                chat_id = data.get("chat_id")
                if not chat_id:
                    continue

                # >>> DEBUG: mostrar payload antes de transformación
                try:
                    print(">>> RAW payload a enviar a Telegram:", json.dumps(data, ensure_ascii=False))
                except Exception:
                    print(">>> RAW payload (no serializable) a enviar a Telegram:", str(data)[:1000])

                # Si existe reply_markup tipo "keyboard" (ReplyKeyboard), convertir a inline
                rm = data.get("reply_markup")
                if isinstance(rm, dict) and "keyboard" in rm:
                    keyboard_rows = rm.get("keyboard", [])
                    inline_rows = []
                    for row in keyboard_rows:
                        # cada 'row' puede ser lista de strings o lista de dicts {"text": ...}
                        inline_row = []
                        for cell in (row or []):
                            if isinstance(cell, dict):
                                label = str(cell.get("text", "") or "")
                            else:
                                label = str(cell or "")
                            if not label:
                                continue
                            # construir callback_data a partir del texto (sanitizado, <=64 chars)
                            cb = re.sub(r"\s+", "_", label.strip().lower())
                            cb = re.sub(r"[^0-9a-zA-Z_]", "", cb)  # quitar caracteres raros
                            if len(cb) == 0:
                                cb = "opt"
                            cb = cb[:64]
                            inline_row.append({"text": label, "callback_data": cb})
                        if inline_row:
                            inline_rows.append(inline_row)
                    if inline_rows:
                        data["reply_markup"] = {"inline_keyboard": inline_rows}
                        print(f">>> Converted ReplyKeyboard -> InlineKeyboard para chat {chat_id}: {inline_rows}")
                    else:
                        # Si no pudimos convertir, mejor remover teclado
                        data["reply_markup"] = {"remove_keyboard": True}
                        print(f">>> ReplyKeyboard no convertible, enviando remove_keyboard para chat {chat_id}")

                # Registrar historial BOT (opcional)
                try:
                    texto_bot = data.get("text") or data.get("caption", "")
                    if chat_id and texto_bot:
                        await registrar_historial(
                            origen="TELEGRAM_BOT",
                            actor="AMI",
                            numero=str(chat_id),
                            texto=str(texto_bot)[:2000]
                        )
                except Exception:
                    pass

                # Enviar finalmente
                await telegram_service.send_message(**data)

            except Exception:
                print("❌ Error enviando mensaje a Telegram (send_telegram_messages)")


    async def send_whatsapp_messages(self, dataList: List[Dict[str, Any]]) -> None:
        """Envía mensajes a WhatsApp (código existente)"""
        # Nota: las variables WHATSAPP_API_URL y HEADERS deben estar definidas en tu entorno/module
        WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL", "")
        HEADERS = {"Authorization": f"Bearer {os.getenv('WHATSAPP_API_TOKEN','')}", "Content-Type": "application/json"}

        for dataItem in dataList:
            try:
                if not isinstance(dataItem, dict):
                    continue

                numero = dataItem.get("to")
                if not numero:
                    continue

                tipo = dataItem.get("type")
                if not tipo:
                    continue

                # Registrar historial BOT
                try:
                    if tipo == "text":
                        texto_bot = dataItem.get("text", {}).get("body")
                    elif tipo == "interactive":
                        inter = dataItem.get("interactive", {})
                        texto_bot = (
                            (inter.get("header") or {}).get("text")
                            or (inter.get("body") or {}).get("text")
                            or (inter.get("action") or {}).get("button")
                        )
                    else:
                        texto_bot = None

                    if numero and texto_bot:
                        try:
                            await registrar_historial(
                                origen="BOT",
                                actor="AMI",
                                numero=numero,
                                texto=str(texto_bot)[:2000]
                            )
                        except Exception:
                            pass
                except Exception:
                    pass

                # Enviar a WhatsApp
                try:
                    resp = requests.post(
                        WHATSAPP_API_URL,
                        headers=HEADERS,
                        json=dataItem,
                        verify=True,
                        timeout=15
                    )
                    try:
                        resp.raise_for_status()
                    except requests.HTTPError as http_err:
                        print(f"❌ Error enviando mensaje a WhatsApp: {http_err} - status {resp.status_code}")
                except Exception:
                    print("❌ Error enviando mensaje a WhatsApp (requests exception)")

            except Exception:
                print("❌ Excepción no esperada en send_whatsapp_messages")
