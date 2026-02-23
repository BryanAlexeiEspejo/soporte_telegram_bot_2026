# app/services/handlers/catastro/D_2_1_info_catastro_2.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

# ✅ Un solo mensaje (LIST) con la respuesta + opciones de navegación
async def manejar_info_catastro_2_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Dónde se encuentra el área de archivo de catastro y cuál es su horario de atención?*\n"
        "R.- Se encuentra ubicado en el edificio Tobía planta baja, su atención a través de la "
        "plataforma de atención al ciudadano de lunes a viernes en los horarios de 08:45 a 16:15 (continuo).\n"
        "------------------------------\n"
    )

    secciones = [{
        "title": "Navegación",
        "rows": [
            {
                "id": "info-catastro-2",
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
        cuerpo=cuerpo,                     # Texto principal (≤1024)
        opciones=secciones,                # 1 sección con 2 filas
        header_text="",                    # no tocar
        footer_text="",                    # no tocar
        button_text="Opciones disponibles" # ≤20
    )

    return [payload]
