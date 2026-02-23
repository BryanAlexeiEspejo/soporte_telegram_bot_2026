# chatbot_handler.py
import os
from typing import List, Dict, Any
from .base_handler import BaseHandler
from app.services.utils.utils_handler import crear_payload_texto
from app.services.feedback.feedback_service import start_feedback_record
from app.database.database import set_estado_usuario

class ChatbotHandler(BaseHandler):
    """Handler simple para iniciar feedback sobre el chatbot (menú 'Calificar Chatbot')."""

    def __init__(self, msg_handler=None):
        super().__init__()
        self.msg_handler = msg_handler

    def get_context_name(self) -> str:
        return "chatbot"

    def get_priority(self) -> int:
        return 5

    async def can_handle(self, texto: str, numero: str, user_state: dict) -> bool:
        # Se activa cuando el usuario elige la opción del menú (id = "calificar_chatbot")
        return texto.strip().lower() in {"calificar chatbot", "calificar_chatbot", "chatbot"}

    async def handle_message(self, texto: str, numero: str, name: str, msg_id: str) -> List[Dict[str, Any]]:
        """
        Inicia el flujo de feedback con flow='chatbot'.
        """
        # Mensaje inicial explicativo
        mensaje = (
            "🗣️ ¡Queremos mejorar! Por favor califica la utilidad del *chatbot*.\n\n"
            "¿La información que te di fue útil?"
        )
        payload = crear_payload_texto(numero, mensaje)

        # Crear registro de feedback directamente con flow='chatbot'
        try:
            feedback_id = start_feedback_record(
                user_id=numero,
                user_name=name,
                question="Calificación del chatbot",
                answer="N/A",
                conversation_id=msg_id,
                flow="chatbot",
                flow_id=None
            )
            # Guardar estado para continuar el flujo (usar la API del dispatcher para setear estado)
            await set_estado_usuario(numero, {"contexto": "feedback", "estado": "waiting_useful", "feedback_id": feedback_id})
        except Exception as e:
            print(f"❌ Error creando feedback chatbot: {e}")

        # Retornar mensaje y que el dispatcher muestre los botones (build_useful_prompt)
        # El dispatcher ya reconoce que está en contexto feedback y preguntará.
        from app.services.feedback.feedback_service import build_useful_prompt
        return [payload, build_useful_prompt(numero)]
