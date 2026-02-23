# app/services/handlers/catastro/D_5_1_info_catastro_5.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

async def manejar_info_catastro_5_1_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Cómo puedo obtener información de una vivienda que no es mi propiedad?*\n"
        "R.- En caso de no acreditar derecho propietario, en el marco de la normativa no se emite información de predios correspondientes a terceras personas.\n"
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
