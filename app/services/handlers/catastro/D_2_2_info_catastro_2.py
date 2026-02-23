# app/services/handlers/catastro/D_2_2_info_catastro_2.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

# ✅ Un solo mensaje (LIST) con la respuesta + opciones de navegación
async def manejar_info_catastro_2_2_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Puedo obtener copias legalizadas en alguna otra plataforma que no sea la de la calle Potosí?*\n"
        "R.- Sí, solo en la calle Potosí, Edificio Tobía, que es el único autorizado "
        "para la emisión de copias o legalizadas de documentos catastrales.\n"
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
