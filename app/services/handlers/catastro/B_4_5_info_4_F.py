from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista
from app.database.database import set_estado_usuario

async def manejar_info_copias_legalizadas_f(numero: str) -> List[Dict]:
    dataList = []

    # ✅ Cuerpo del mensaje
    cuerpo = (
        "*¿Qué obtengo al hacer este trámite?*\n\n"
        "El ciudadano obtiene una copia oficial que tiene el mismo valor legal que el original, "
        "permitiéndole realizar trámites o presentarlas como prueba en diversos procesos."
    )

    secciones = [
        {
            "title": "Información útil",
            "rows": [
                {"id": "rcl-info-b", "title": "Dónde se realiza", "description": "¿Dónde se realiza el trámite?"},
                {"id": "rcl-info-c", "title": "Qué es", "description": "¿Qué es una copia legalizada?"},
                {"id": "rcl-info-d", "title": "Para qué sirve", "description": "¿Para qué sirve un certificado de registro catastral?"},
                {"id": "rcl-info-e", "title": "Costo", "description": "¿Tiene un costo este trámite?"},
                {"id": "rcl-info-f", "title": "Resultado", "description": "¿Qué obtengo al hacer este trámite?"},
                {"id": "rcl-info-g", "title": "Quién puede realizarlo", "description": "¿Quién puede realizar este trámite?"}
            ]
        },
        {
            "title": "Navegación",
            "rows": [
                {"id": "rcl", "title": "⬅️ Volver", "description": "Volver al menú anterior"},
                {"id": "inicio", "title": "🏠 Inicio", "description": "Volver al inicio"}
            ]
        }
    ]

    # ✅ Crear lista tipo WhatsApp
    payload_lista = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text="📘 Copias Legalizadas",
        footer_text="",
        button_text="Opciones disponibles"
    )
    dataList.append(payload_lista)

    # ✅ Guardar estado del usuario
    await set_estado_usuario(numero, {
        "contexto": "catastro",
        "estado": "copias-legalizadas-info-f"
    })

    return dataList
