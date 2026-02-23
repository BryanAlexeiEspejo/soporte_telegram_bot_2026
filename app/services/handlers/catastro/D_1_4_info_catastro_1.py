# app/services/handlers/catastro/D_1_info_catastro_1_respuesta_4.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

# ✅ Un solo mensaje (LIST) con la respuesta + opciones de navegación
async def manejar_info_catastro_4_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Qué es la georreferenciación en el catastro?*\n"
        "R.- Es la localización precisa de cualquier lugar de la superficie "
        "terrestre en un mapa con coordenadas geográficas mediante uso de "
        "instrumentos de posicionamiento geodésico, a fin de establecer su "
        "ubicación exacta.\n"
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
