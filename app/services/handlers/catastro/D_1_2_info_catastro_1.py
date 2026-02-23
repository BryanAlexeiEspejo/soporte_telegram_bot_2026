# app/services/handlers/catastro/D_1_info_catastro_1_respuesta_2.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

# ✅ Respuesta a: "¿Qué es un bien inmueble o predio?"
# En un solo mensaje LIST con opciones de navegación (Menú anterior / Inicio)
async def manejar_info_catastro_2_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Qué es un bien inmueble o predio?*\n"
        "R.- Un bien inmueble o predio es una propiedad fija que no puede "
        "ser trasladada de un lugar a otro sin alterar su naturaleza o esencia. "
        "Está ligado al suelo de manera permanente y tiene características "
        "físicas, legales y económicas que lo hacen único.\n"
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
        cuerpo=cuerpo,          # ≤1024
        opciones=secciones,     # 1 sección con 2 filas
        header_text="",         # sin header
        footer_text="",         # sin footer
        button_text="Opciones"  # ≤20
    )

    return [payload]
