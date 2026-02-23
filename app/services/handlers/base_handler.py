import re
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class BaseHandler(ABC):
    """Clase base para todos los handlers de mensajes"""
    
    @abstractmethod
    async def can_handle(self, texto: str, numero: str, user_state: dict) -> bool:
        """¿Puede este handler procesar el mensaje?"""
        pass
    
    @abstractmethod
    async def handle_message(self, texto: str, numero: str, name: str, msg_id: str) -> List[Dict[str, Any]]:
        """Procesa el mensaje y retorna payloads"""
        pass
    
    @abstractmethod
    def get_context_name(self) -> str:
        """Nombre del contexto para este handler"""
        pass
    
    def get_priority(self) -> int:
        """Prioridad del handler (menor = mayor prioridad)"""
        return 50
    