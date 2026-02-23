from typing import List, Dict
from app.database.database import set_estado_usuario
from app.services.whatsapp_template import crear_payload_lista

async def manejar_reclamo_catastro(numero: str) -> List[Dict]:
    dataList = []

    cuerpo = (
        "📢 *Quiero hacer un reclamo en temas catastrales*\n\n"
        "✅ Para hacer un reclamo, debes dirigirte a:\n"
        "*Plataforma ACM Edif. Tobia*, planta baja, calle Potosí casi esq. Colón.\n"
        "🕒 Horario de atención: *8:45 a 16:15 hrs.*\n\n"
        "📍 *Ver mapa:* https://maps.app.goo.gl/aiTLfYVm5pUhCN5Q8\n\n"
        "✅ Asegúrate de tener a mano toda la documentación que respalde tu reclamo "
        "o cualquier evidencia que pueda ayudar a aclarar tu situación.\n\n"
      
    )

    secciones = [
        {
            "title": "📋 Opciones disponibles",
            "rows": [
                {
                    "id": "denuncia-construccion",
                    "title": "🏗️ Denunciar construcción",
                    "description": "Dónde puedo denunciar la construcción de una casa"
                },
                {
                    "id": "denuncia-avs",
                    "title": "🚧 Avasallamiento",
                    "description": "Quiero denunciar el avasallamiento de terreno municipal"
                }
            ]
        },
        {
            "title": "🔁 Navegación",
            "rows": [
                {
                    "id": "catastro-b",
                    "title": "📑 Ver requisitos",
                    "description": "Ver requisitos de trámites catastrales"
                },
                {
                    "id": "inicio",
                    "title": "🏠 Volver al inicio",
                    "description": "Ir al menú principal de AMI"
                }
            ]
        }
    ]

    payload_lista = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text="📘 Reclamo Catastral",
        footer_text="AMI Catastro",
        button_text="Opciones disponibles"
    )

    dataList.append(payload_lista)

    await set_estado_usuario(numero, {
        "contexto": "catastro",
        "estado": "reclamo-catastro"
    })

    return dataList
