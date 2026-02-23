# app/services/handlers/catastro/D_3_1_info_catastro_3.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

# ✅ Un solo mensaje (LIST) con la respuesta + navegación
async def manejar_info_catastro_3_1_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Qué tipos de bienes inmuebles están sujetos a registro catastral?*\n"
        "R.- Inmuebles de propiedad unifamiliar, inmuebles de propiedad "
        "horizontal y de dominio público municipal.\n"
        "------------------------------\n"
    )

    secciones = [{
        "title": "Navegación",
        "rows": [
            { "id": "info-catastro-3", "title": "⬅️ Menú anterior", "description": "Volver a preguntas 1–8" },
            { "id": "inicio",          "title": "🏠 Inicio",        "description": "Ir al menú principal" }
        ]
    }]

    payload = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,                  # Texto principal (≤1024)
        opciones=secciones,             # 1 sección con 2 filas
        header_text="",                 # no tocar
        footer_text="",                 # no tocar
        button_text="Opciones disponibles"  # ≤20
    )
    return [payload]
