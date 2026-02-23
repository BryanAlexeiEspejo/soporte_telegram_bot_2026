# app/services/handlers/catastro/D_1_info_catastro_1_respuesta_9.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

# ✅ Un solo mensaje (LIST) con la respuesta + opciones de navegación
async def manejar_info_catastro_9_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Cuáles son los beneficios de tener un inmueble registrado en el catastro?*\n"
        "R.- Registrar un inmueble en el catastro trae múltiples beneficios "
        "legales, fiscales, administrativos y de planificación.\n"
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
        cuerpo=cuerpo,                   # Texto principal (≤1024)
        opciones=secciones,              # 1 sección con 2 filas
        header_text="",                  # no tocar
        footer_text="",                  # no tocar
        button_text="Opciones disponibles"  # ≤20
    )

    return [payload]
