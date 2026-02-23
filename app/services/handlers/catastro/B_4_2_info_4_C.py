from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista
from app.database.database import set_estado_usuario

async def manejar_info_copias_legalizadas_c(numero: str) -> List[Dict]:
    dataList = []

    # ✅ Texto explicativo incluido directamente en el cuerpo de la lista
    cuerpo = (
        "📄 *¿Qué es una copia legalizada?*\n\n"
        "Una *copia legalizada* es una fotocopia de un documento original que ha sido certificada por la autoridad competente, "
        "asegurando que coincide fielmente con el original.\n\n"
       
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

    payload_lista = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text="📘 Copias Legalizadas",
        footer_text="",
        button_text="Opciones disponibles"
    )
    dataList.append(payload_lista)

    await set_estado_usuario(numero, {
        "contexto": "catastro",
        "estado": "copias-legalizadas-info-c"
    })

    return dataList
