# app/services/handlers/catastro/B_3_4_info_3_E.py

from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista
from app.database.database import set_estado_usuario

async def manejar_info_actualizacion_e(numero: str) -> List[Dict]:
    dataList = []

    cuerpo = (
        "💰 *¿Tiene un costo?*\n\n"
        "Sí, el trámite tiene un costo de *54.10 Bs.* al mes de *diciembre de 2025*.\n\n"
        "📍 El costo puede estar sujeto a actualizaciones, por lo que se recomienda verificarlo directamente en:\n"
        "• Las plataformas de atención ciudadana\n"
        "• La *Autoridad Catastral Municipal (ACM)*\n\n"
       
    )

    header = "📘 Actualización del Registro Catastral"
    footer = ""

    secciones = [
        {
            "title": "Información útil",
            "rows": [
                {"id": "ar-info-b", "title": "¿Dónde?", "description": "¿Dónde se realiza este trámite?"},
                {"id": "ar-info-c", "title": "Definición", "description": "¿Qué es una actualización de registro catastral?"},
                {"id": "ar-info-d", "title": "Finalidad", "description": "¿Para qué sirve un certificado de registro catastral?"},
                {"id": "ar-info-e", "title": "Costo", "description": "¿Tiene un costo?"},
                {"id": "ar-info-f", "title": "Resultado", "description": "¿Qué obtengo con este trámite?"},
                {"id": "ar-info-g", "title": "Quiénes", "description": "¿Quién puede realizar este trámite?"}
            ]
        },
        {
            "title": "🔁 Navegación",
            "rows": [
                {"id": "catastro-b", "title": "⬅️ Volver", "description": "Volver al menú anterior"},
                {"id": "inicio", "title": "🏠 Inicio", "description": "Volver al Inicio"}
            ]
        }
    ]


    payload_menu = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text=header,
        footer_text=footer,
        button_text="Opciones disponibles"
    )

    dataList.append(payload_menu)

    await set_estado_usuario(numero, {
        "contexto": "catastro",
        "estado": "actualizacion-registro-info-e"
    })

    return dataList
