from typing import List, Dict
from app.database.database import set_estado_usuario
from app.services.whatsapp_template import crear_payload_lista

async def manejar_info_certificado_pu_b(numero: str) -> List[Dict]:
    dataList = []

    cuerpo = (
        "*¿Dónde se realiza este trámite?*\n\n"
        "✅ *Orientación sobre los requisitos y pasos a seguir:*\n\n"
        "*📍 CALLE POTOSÍ*\n"
        "• Oficinas: Potosí y Colón, Edificio Tobia.\n"
        "• Plataforma de atención ciudadana.\n"
        "• 📍 Cómo llegar: https://maps.app.goo.gl/aiTLfYm5pUhCN5Q8\n\n"
        "*📍 PIAC SUR*\n"
        "• Av. Gral. José Ballivián Nº720, Planta Baja, Edif. ATLANTA.\n"
        "• Horario: 8:45 a 16:15 hrs. (continuo).\n"
        "• 📍 Cómo llegar: https://maps.app.goo.gl/513bab6Yy9iusifVo9\n\n"
        "✅ *Ingresar y recoger trámites:*\n\n"
        "*📍 CAMACHO*\n"
        "• Centro Comercial Camacho, Nivel 1.\n"
        "• Horario: 8:45 a 16:15 hrs. (continuo).\n"
        "• 📍 Cómo llegar: https://maps.app.goo.gl/XQtRE17M7SnFHT596\n\n"
        "*📍 SUR (PIAC)*\n"
        "• Av. Ballivián Nº720, Edif. ATLANTA (mismo lugar que PIAC).\n"
        "• 📍 Cómo llegar: https://maps.app.goo.gl/513bab6Yy9iusifVo9\n\n"
        "*📍 MIRAFLORES*\n"
        "• Calle Chichas esq. Juan de Vargas, Edif. ESPRA PB, Z. Miraflores.\n"
        "• 📍 Cómo llegar: https://maps.app.goo.gl/DqS8UsMUqbxmixjR9\n\n"
     
    )

    header = ""
    footer = ""

    secciones = [
        {
            "title": "Información útil",
            "rows": [
                {"id": "info-a", "title": "Sin testimonio", "description": "¿Que pasa si no tiene el testimonio de propiedad (original y fotocopia)?"},
                {"id": "info-b", "title": "¿Dónde?", "description": "¿Dónde se realiza el trámite?"},
                {"id": "info-c", "title": "Definición", "description": "¿Qué es un certificado de registro catastral?"},
                {"id": "info-d", "title": "Finalidad", "description": "¿Para que sirve el certificado de registro catastral?"},
                {"id": "info-e", "title": "Costo", "description": "¿Tiene un costo?"},
                {"id": "info-f", "title": "Resultado", "description": "¿Qué obtengo al hacer este trámite?"},
                {"id": "info-g", "title": "Quiénes", "description": "¿Quién puede realizar este trámite?"},
            ],
        },
        {
            "title": "Navegación",
            "rows": [
                {
                    "id": "req-catastro-1",
                    "title": "⬅️ Volver",
                    "description": "Volver al menú anterior"
                },
                {
                    "id": "inicio",
                    "title": "🏠 Inicio",
                    "description": "Volver al Inicio"
                }
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
        "estado": "certificado-opcion"
    })

    return dataList
