# app/services/handlers/catastro/D_4_3_info_catastro_4.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

# ✅ Respuesta 4-3
async def manejar_info_catastro_4_3_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Qué debo hacer si mi inmueble no está correctamente representado en la cartografía catastral?*\n"
        "R.- Debe solicitar una actualización de corrección de datos adjuntando "
        "los requisitos establecidos en la normativa vigente a través de las "
        "plataformas de atención al ciudadano.\n"
        "------------------------------\n"
    )

    secciones = [{
        "title": "Navegación",
        "rows": [
            {"id": "info-catastro-4", "title": "⬅️ Menú anterior", "description": "Volver a preguntas 1–3"},
            {"id": "inicio",          "title": "🏠 Inicio",        "description": "Ir al menú principal"},
        ]
    }]

    payload = await crear_payload_lista(
        numero=numero, cuerpo=cuerpo, opciones=secciones,
        header_text="", footer_text="", button_text="Opciones disponibles"
    )
    return [payload]
