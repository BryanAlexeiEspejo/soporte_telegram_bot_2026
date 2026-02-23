# app/services/handlers/catastro/D_1_info_catastro_1_respuesta_6.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

# ✅ Un solo mensaje (LIST) con la respuesta + opciones de navegación
async def manejar_info_catastro_6_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Qué es un conflicto de sobreposición catastral?*\n"
        "R.- Es un conflicto de derecho propietario entre particulares con "
        "relación a la posesión física de un bien inmueble.\n"
        "------------------------------\n"
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
        cuerpo=cuerpo,                 # Texto principal (≤1024)
        opciones=secciones,            # 1 sección con 2 filas
        header_text="",                # no tocar
        footer_text="",                # no tocar
        button_text="Opciones disponibles"  # ≤20
    )

    return [payload]
