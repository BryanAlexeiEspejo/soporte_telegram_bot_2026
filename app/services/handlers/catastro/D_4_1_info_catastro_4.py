# app/services/handlers/catastro/D_4_1_info_catastro_4.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

# ✅ Respuesta 4-1
async def manejar_info_catastro_4_1_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Cómo se calcula el valor catastral de mi propiedad?*\n"
        "R.- Para el cálculo del valor catastral de los bienes inmuebles o "
        "predios, se utilizará el Plano de Zonificación y Valuación Zonal del "
        "municipio de La Paz y las Tablas de Valores de Suelo y Construcciones, "
        "aprobadas por el Concejo Municipal.\n"
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
