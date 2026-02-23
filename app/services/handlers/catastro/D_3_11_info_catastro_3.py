# app/services/handlers/catastro/D_3_11_info_catastro_3.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

async def manejar_info_catastro_3_11_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Cuál es el procedimiento para solicitar fotocopias legalizadas de levantamientos topográficos?*\n"
        "R.- Realizar una nota dirigida al director de la Autoridad Catastral Municipal, "
        "especificando el Código Catastral y el número de copias que requiera.\n"
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
