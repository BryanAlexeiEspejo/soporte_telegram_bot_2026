from typing import List, Dict
from app.database.database import set_estado_usuario
from app.services.whatsapp_template import crear_payload_lista

async def manejar_copias_legalizadas(numero: str) -> List[Dict]:
    dataList = []

    # ✅ Cuerpo del mensaje principal
    cuerpo = (
        "📄 *Requisitos para copias legalizadas:*\n"
        "• Fotocopia de tu cédula de identidad (C.I.).\n"
        "• Fotocopia del folio del inmueble.\n"
        "• Fotocopia del último impuesto pagado.\n"
        "• Presenta tu solicitud y completa el Formulario Único de Solicitud (FUS) en el lugar.\n\n"
        "📍 *Lugar:* Plataforma de la calle Potosí.\n\n"
        "📚 *Recursos:*\n"
        "• Fichas catastrales A, B, C.\n"
        "• Normativa y leyes municipales catastrales.\n"
    )

    # ✅ Secciones del menú
    secciones = [
        {
            "title": "Información útil",
            "rows": [
                {"id": "rcl-info-b", "title": "Dónde se realiza", "description": "¿Dónde se realiza el trámite?"},
                {"id": "rcl-info-c", "title": "Qué es", "description": "¿Que es una copia legalizada?"},
                {"id": "rcl-info-d", "title": "Para qué sirve", "description": "¿Para que sirve un certificado de registro catastral?"},
                {"id": "rcl-info-e", "title": "Costo", "description": "¿Tiene un costo este trámite?"},
                {"id": "rcl-info-f", "title": "Resultado", "description": "¿Qué obtengo al hacer este trámite?"},
                {"id": "rcl-info-g", "title": "Quién puede realizarlo", "description": "¿Quién puede realizar este trámite?."}
            ]
        },
        {
            "title": "Recursos adicionales",
            "rows": [
                {"id": "info-fichas", "title": "📥 Fichas A, B, C", "description": "Descargar fichas catastrales."},
                {"id": "info-leyes", "title": "📘 Normativa catastral", "description": "Ver leyes y normativa municipal de catastro."}
            ]
        },
        {
            "title": "Navegación",
            "rows": [
                {"id": "catastro-b", "title": "⬅️ Volver", "description": "Regresar al menú anterior."},
                {"id": "inicio", "title": "🏠 Inicio", "description": "Volver al menú principal de AMI."}
            ]
        }
    ]

    # ✅ Crear el menú interactivo
    payload_menu = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text="📘 Copias Legalizadas",
        footer_text="",
        button_text="Ver opciones"
    )

    dataList.append(payload_menu)

    # ✅ Guardar estado del usuario
    await set_estado_usuario(numero, {
        "contexto": "catastro",
        "estado": "copias-legalizadas-preguntas"
    })

    return dataList
