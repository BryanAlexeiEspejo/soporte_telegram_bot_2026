# app/services/handlers/catastro/B_3_2_info_3_C.py

from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista
from app.database.database import set_estado_usuario

async def manejar_info_actualizacion_c(numero: str) -> List[Dict]:
    dataList = []

    cuerpo = (
        "📄 *¿Qué es una actualización de registro catastral?*\n\n"
        "La actualización es la *modificación del registro catastral automatizado* y del Certificado vigente "
        "cuando existen *cambios técnicos* (como número de puerta o ubicación) o de *derecho propietario* (por ejemplo, "
        "cambio de nombre o superficie legal), *sin alterar la forma ni la construcción* del predio.\n\n"
      
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
        "estado": "actualizacion-registro-info-c"
    })

    return dataList
