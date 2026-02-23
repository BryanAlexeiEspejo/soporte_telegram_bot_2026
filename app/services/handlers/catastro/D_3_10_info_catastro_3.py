# app/services/handlers/catastro/D_3_10_info_catastro_3.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

async def manejar_info_catastro_3_10_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Puedo solicitar una copia original de mi certificado catastral?*\n"
        "R.- Se puede otorgar una copia simple del Certificado de registro Catastral. "
        "Puede también solicitar un duplicado o una actualización en caso de requerir un ejemplar original.\n"
        "------------------------------\n"
    )

    secciones = [{
        "title": "Navegación",
        "rows": [
            {"id": "info-catastro-3-p2", "title": "⬅️ Menú anterior", "description": "Volver a preguntas 9–12"},
            {"id": "inicio",             "title": "🏠 Inicio",        "description": "Ir al menú principal"},
        ]
    }]

    payload = await crear_payload_lista(
        numero=numero, cuerpo=cuerpo, opciones=secciones,
        header_text="", footer_text="", button_text="Opciones disponibles"
    )
    return [payload]
