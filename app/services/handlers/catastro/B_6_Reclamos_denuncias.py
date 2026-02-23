from typing import List, Dict
from app.database.database import set_estado_usuario
from app.services.whatsapp_template import crear_payload_lista

async def manejar_reclamos_denuncias(numero: str) -> List[Dict]:
    dataList = []

    cuerpo = (
        "📣 *Reclamos y denuncias*\n\n"
        "Si tienes algún tipo de reclamo o denuncia,\n"
        "selecciona una de las opciones disponibles que tenemos:\n\n"
       
    )

    secciones = [
        {
            "title": "Tipos de reclamos",
            "rows": [
                {
                    "id": "reclamo-catastro",
                    "title": "1. Reclamo catastral",
                    "description": "Quiero hacer un reclamo en temas catastrales."
                },
                {
                    "id": "denuncia-construccion",
                    "title": "2. Denuncia construcción",
                    "description": "Dónde puedo denunciar la construcción de una casa."
                },
                {
                    "id": "denuncia-avs",
                    "title": "3. Avasallamiento",
                    "description": "Quiero denunciar el avasallamiento de terreno municipal."
                }
            ]
        },
        {
            "title": "Navegación",
            "rows": [
                {
                    "id": "catastro-b",
                    "title": "📑 Requisitos",
                    "description": "Ver requisitos de trámites catastrales"
                },
                {
                    "id": "catastro-c",
                    "title": "🕐 Puntos de atención",
                    "description": "Horarios y oficinas disponibles"
                },
                {
                    "id": "inicio",
                    "title": "🏠 Inicio",
                    "description": "Volver al menú principal"
                }
            ]
        }
    ]

    try:
        payload = await crear_payload_lista(
            numero=numero,
            cuerpo=cuerpo,
            opciones=secciones,
            header_text="",
            footer_text="AMI Catastro",
            button_text="Opciones disponibles"
        )
        dataList.append(payload)

        await set_estado_usuario(numero, {
            "contexto": "catastro",
            "estado": "reclamos-denuncias"
        })

    except Exception as e:
        print("❌ Error generando payload de reclamos:", e)

    return dataList
