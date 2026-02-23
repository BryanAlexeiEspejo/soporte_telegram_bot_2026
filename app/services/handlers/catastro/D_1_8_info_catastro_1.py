# app/services/handlers/catastro/D_1_info_catastro_1_respuesta_8.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

# ✅ Un solo mensaje (LIST) con la respuesta + opciones de navegación
async def manejar_info_catastro_8_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Qué son los bienes de dominio municipal?*\n"
        "R.- Los bienes de dominio municipal son aquellos bienes inmuebles y "
        "muebles que pertenecen al municipio y están destinados a un uso "
        "público o al cumplimiento de las funciones administrativas y de "
        "servicio del gobierno local.\n"
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
