# app/services/handlers/catastro/D_4_2_info_catastro_4.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

# ✅ Respuesta 4-2
async def manejar_info_catastro_4_2_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Cómo afecta el uso del suelo al valor catastral de mi propiedad?*\n"
        "R.- Para el valor catastral no se considera un factor a calcular el uso de suelo.\n"
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
