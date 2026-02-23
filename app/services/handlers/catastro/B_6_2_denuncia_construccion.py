from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista
from app.database.database import set_estado_usuario

async def manejar_denuncia_construccion(numero: str) -> List[Dict]:
    dataList = []

    cuerpo = (
        "🏗️ *¿Dónde puedo denunciar la construcción de una casa?*\n\n"
        "✅ Debes dirigirte a la *subalcaldía de tu distrito* para presentar tu denuncia "
        "de forma presencial ante la autoridad correspondiente.\n\n"
      
    )

    secciones = [
        {
            "title": "📋 Opciones disponibles",
            "rows": [
                {
                    "id": "reclamo-catastro",
                    "title": "📢 Hacer un reclamo",
                    "description": "Quiero hacer un reclamo en temas catastrales"
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
        header_text="📘 Denuncia Construcción",
        footer_text="AMI Catastro",
        button_text="Opciones disponibles"
    )

    dataList.append(payload_lista)

    await set_estado_usuario(numero, {
        "contexto": "catastro",
        "estado": "denuncia-construccion"
    })

    return dataList
