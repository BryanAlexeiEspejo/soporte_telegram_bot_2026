from app.database.database import set_estado_usuario
from app.services.whatsapp_template import crear_payload_lista
from typing import List, Dict

async def manejar_requisitos_catastro(numero: str) -> List[Dict]:
    dataList = []

    # Texto del cuerpo igual a la imagen proporcionada
    cuerpo = (
        "*Requisitos para trámites en catastro:*\n"
        "Aquí encontrarás los requisitos necesarios para realizar los siguientes trámites:\n"
        "• Certificado de registro catastral.\n"
        "• Duplicado de certificado catastral.\n"
        "• Actualización del registro catastral a solicitud directa.\n"
        "• Copias legalizadas.\n"
        "• Emisión de certificado de registro catastral en el marco de la Ley 247.\n"
        "• Reclamos y denuncias.\n"
        "👉 Elige una opción de la lista para conocer los requisitos:"
    )

    header = "📋 Requisitos Catastro"
    footer = ""  # sin footer

    seccion_principal = {
        "title": "Trámites disponibles",
        "rows": [
            {"title": "Certificado registro", "id": "req-catastro-1", "description": "Trámite por primera vez"},
            {"title": "Duplicado certificado", "id": "req-catastro-2", "description": "Reposición por extravío"},
            {"title": "Actualización registro", "id": "req-catastro-3", "description": "Cambio de datos catastrales"},
            {"title": "Copias legalizadas", "id": "req-catastro-4", "description": "Documentos oficiales"},
            {"title": "Certif. Ley 247", "id": "req-catastro-5", "description": "Ley de regularización"},
            {"title": "Reclamos y denuncias", "id": "req-catastro-6", "description": "Reportar irregularidades"},
        ],
    }

    seccion_navegacion = {
        "title": "Navegación",  
        
        "rows": [
            {"id": "catastro-b", "title": "⬅️ Volver", "description": "Volver a información catastral"},
            {"id": "inicio", "title": "🏠 Inicio", "description": "Volver al inicio"},
        ],
    }

    payload = await crear_payload_lista(
        numero,
        cuerpo,
        [seccion_principal, seccion_navegacion],
        header,
        footer,
        "Ver requisitos",
    )

    dataList.append(payload)
    await set_estado_usuario(numero, {"contexto": "catastro", "estado": "requisitos-catastro"})
    return dataList
