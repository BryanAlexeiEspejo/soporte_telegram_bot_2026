# app/services/handlers/catastro/D_3_3_info_catastro_3.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

async def manejar_info_catastro_3_3_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Qué es el código catastral y para qué sirve?*\n"
        "R.- Es la identificación numérica única e irrepetible asignada a "
        "cada predio urbano o unidad de propiedad horizontal, que resulta "
        "del proceso de catastración, que sirve para ubicación inequívoca "
        "de un bien inmueble.\n"
        "------------------------------\n"
    )
    secciones = [{
        "title": "Navegación",
        "rows": [
            {"id": "info-catastro-3", "title": "⬅️ Menú anterior", "description": "Volver a preguntas 1–8"},
            {"id": "inicio",          "title": "🏠 Inicio",        "description": "Ir al menú principal"},
        ],
    }]
    payload = await crear_payload_lista(numero=numero, cuerpo=cuerpo, opciones=secciones,
                                        header_text="", footer_text="", button_text="Opciones disponibles")
    return [payload]
