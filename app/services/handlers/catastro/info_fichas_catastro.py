from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista
from app.database.database import set_estado_usuario

async def manejar_info_fichas(numero: str) -> List[Dict]:
    dataList = []

    cuerpo = (
        "*Descargar fichas catastrales A, B, C.*\n"
        "Tenemos los siguientes archivos para que puedas descargarlos:\n\n"
        "*Ficha Catastral A* Propiedad Unifamiliar – ACM:\n"
        "https://catastro.lapaz.bo/download/ficha-catastral-a-propiedad-unifamiliar-acm/\n\n"
        "*Ficha Catastral B* Matriz PH – ACM:\n"
        "https://catastro.lapaz.bo/download/ficha-catastral-b-matriz-ph-acm/\n\n"
        "*Ficha Catastral C* Unidad PH – ACMC:\n"
        "https://catastro.lapaz.bo/download/ficha-catastral-c-unidad-ph-acmc/\n\n"
   
    )

    # ✅ Menú tipo lista con navegación
    secciones = [
        {
            "title": "🔁 Navegación",
            "rows": [
                {
                    "id": "catastro-b",  # ID que tú controles en tu handler
                    "title": "⬅️ Volver",
                    "description": "Ver requisitos de tramites catastrales"
                },
                {
                    "id": "inicio",
                    "title": "🏠 Inicio",
                    "description": "Volver al inicio"
                }
            ]
        }
    ]

    payload = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text="📘 Fichas Catastrales",
        footer_text="",
        button_text="Opciones disponibles"
    )

    dataList.append(payload)

    await set_estado_usuario(numero, {
        "contexto": "catastro",
        "estado": "fichas-catastro"
    })

    return dataList
