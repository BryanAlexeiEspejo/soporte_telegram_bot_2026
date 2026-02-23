from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista
from app.database.database import set_estado_usuario

async def manejar_info_actualizacion_b(numero: str) -> List[Dict]:
    dataList = []

    cuerpo = (
        "📍 *¿Dónde se realiza el trámite?*\n\n"
        "✅ *Orientación sobre requisitos y pasos:*\n"
        "• Oficinas de la *calle Potosí y Colón*, Edif. Tobia – Plataforma de atención ciudadana.\n"
        "• 🕘 *Horario:* 8:45 a 16:15 (continuo)\n"
        "• 🗺️ *Cómo llegar:* https://maps.app.goo.gl/aiTLfYVm5pUhCN5Q8\n\n"
        "✅ *Ingreso y retiro del trámite:*\n"
        "• *En calle Potosí y Colón* (Plataforma Edif. Tobia)\n"
        "• 🕘 8:45 a 16:15 (continuo)\n"
        "• 🗺️ *Cómo llegar:* https://maps.app.goo.gl/aiTLfYVm5pUhCN5Q8\n\n"
        "📍 *Zona Sur:*\n"
        "• Av. Gral. José Ballivián Nº720, Planta Baja, Edif. ATLANTA.\n"
        "• 🕘 *Horario:* 8:45 a 15:30 (continuo)\n"
        "• 🗺️ *Cómo llegar:* https://maps.app.goo.gl/513bab6Yy9iusifVo9\n\n"
      
    )

    header = "📘 Dónde realizar el trámite"
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
        "estado": "actualizacion-registro-info-b"
    })

    return dataList
