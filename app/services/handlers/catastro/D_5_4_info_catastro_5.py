# app/services/handlers/catastro/D_5_4_info_catastro_5.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

async def manejar_info_catastro_5_4_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Qué debo hacer si hay contradicciones en los documentos de propiedad debido a un divorcio?*\n"
        "R.- Deberá acudir a las instancias jurídicas correspondientes que emitieron dichos documentos.\n"
        "------------------------------\n"
    )
    secciones = [{
        "title": "Navegación",
        "rows": [
            {"id": "info-catastro-5", "title": "⬅️ Menú anterior", "description": "Volver a preguntas 1–6"},
            {"id": "inicio",          "title": "🏠 Inicio",        "description": "Ir al menú principal"},
        ],
    }]
    payload = await crear_payload_lista(numero=numero, cuerpo=cuerpo, opciones=secciones,
                                        header_text="", footer_text="", button_text="Opciones disponibles")
    return [payload]
