from typing import List, Dict
from app.database.database import set_estado_usuario
from app.services.whatsapp_template import crear_payload_lista

async def manejar_info_certificado_pu_d(numero: str) -> List[Dict]:
    dataList = []

    cuerpo = (
        "*¿Para qué sirve un certificado de registro catastral?*\n\n"
        "El Certificado de Registro Catastral es un documento oficial emitido por la Autoridad Catastral Municipal "
        "que acredita la existencia y registro de un inmueble en el sistema catastral del municipio.\n\n"
        "Este documento tiene múltiples usos y es esencial en diferentes situaciones legales, administrativas y personales, "
        "facilitando su gestión para operaciones en el GAMLP, Derechos Reales y entidades financieras.\n\n"
     
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
