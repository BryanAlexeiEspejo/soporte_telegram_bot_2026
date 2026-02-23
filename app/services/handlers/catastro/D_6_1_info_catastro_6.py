# app/services/handlers/catastro/D_6_1_info_catastro_6.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

async def manejar_info_catastro_6_1_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Qué debo hacer si hay una sobreposición de mi terreno con el de mi vecino?*\n"
        "R.- En caso de existir sobreposicion con predios vecinos deberá solucionar en la vía judicial correspondiente al tratarse de un conflicto entre particulares.\n"
        "------------------------------\n"
    )
    secciones = [{
        "title": "Navegación",
        "rows": [
            {"id": "info-catastro-6", "title": "⬅️ Menú anterior", "description": "Volver a preguntas 1–7"},
            {"id": "inicio",          "title": "🏠 Inicio",        "description": "Ir al menú principal"},
        ],
    }]
    payload = await crear_payload_lista(numero=numero, cuerpo=cuerpo, opciones=secciones,
                                        header_text="", footer_text="", button_text="Opciones disponibles")
    return [payload]
