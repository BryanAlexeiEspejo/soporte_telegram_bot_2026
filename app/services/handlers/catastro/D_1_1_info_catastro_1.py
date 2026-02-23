# app/services/handlers/catastro/D_1_info_catastro_1_respuesta.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

# ✅ Un solo mensaje (LIST) con la respuesta + opciones de navegación
async def manejar_info_catastro_1_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Qué es el catastro municipal?*\n"
        "R.- Es el inventario físico de los bienes inmuebles dentro la "
        "jurisdicción del municipio de La Paz.\n"
        "------------------------------\n\n"
    )

    secciones = [{
        "title": "Navegación",
        "rows": [
            {
                "id": "info-catastro-1",
                "title": "⬅️ Menú anterior",
                "description": "Volver a preguntas"
            },
            {
                "id": "inicio",
                "title": "🏠 Inicio",
                "description": "Ir al menú principal"
            }
        ]
    }]

    payload = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,               # Texto principal (≤1024)
        opciones=secciones,          # 1 sección con 2 filas
        header_text="",     # opcional; déjalo "" si tu helper no lo soporta
        footer_text="",  # ≤60
        button_text="Opciones disponibles"       # ≤20
    )

    return [payload]
