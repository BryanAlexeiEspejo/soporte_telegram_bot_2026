# app/services/handlers/catastro/B_4_1_info_4_B.py

from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista
from app.database.database import set_estado_usuario

async def manejar_info_copias_legalizadas_b(numero: str) -> List[Dict]:
    dataList = []

    cuerpo = (
        "*📍 ¿Dónde se realiza este trámite?*\n\n"
        "✅ *Orientación sobre los requisitos y pasos a seguir:*\n"
        "• Oficinas de la *calle Potosí y Colón*, edificio Tobia, plataforma de atención ciudadana.\n"
        "• *Horario:* 8:45 hrs. a 16:15 hrs. (horario continuo).\n"
        "• *Cómo llegar:* https://maps.app.goo.gl/aiTLfYVm5pUhCN5Q8\n\n"
        "✅ *Ingresar y recoger trámites:*\n"
        "• Oficinas de la *calle Potosí y Colón*, edificio Tobia, plataforma de atención ciudadana.\n"
        "• *Horario:* 8:45 hrs. a 16:15 hrs. (horario continuo).\n"
        "• *Cómo llegar:* https://maps.app.goo.gl/aiTLfYVm5pUhCN5Q8\n\n"
        "📌 Si cuentas con todos los documentos requeridos, solicita una ficha para *“Copias Legalizadas”* "
        "en el dispensador de fichas en esta plataforma."
    )

    header = "📘 Copias Legalizadas"
    footer = "AMI Catastro"

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
        "estado": "copias-legalizadas-info-b"
    })

    return dataList
