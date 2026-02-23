from typing import List, Dict
from app.database.database import set_estado_usuario
from app.services.whatsapp_template import crear_payload_lista

async def manejar_info_certificado_pu_g(numero: str) -> List[Dict]:
    dataList = []

    cuerpo = (
        "*¿Quién puede realizar este trámite?*\n\n"
        "• El propietario del inmueble.\n"
        "• Un apoderado legal, presentando el poder notarial correspondiente.\n\n"
        "*ℹ️ ¿Puedo realizar el trámite en nombre de otra persona?*\n\n"
        "Sí, puedes realizar el trámite en nombre de otra persona si presentas un poder notarial que te autorice a hacerlo.\n\n"
        "*📌 Importante:*\n"
        "• Si el propietario ha fallecido, los herederos deben realizar primero la declaratoria de herederos para poder actualizar los datos del catastro.\n"
        "• En casos de propiedad compartida (varios propietarios), cualquiera de los copropietarios puede hacer el trámite, siempre que tenga los documentos requeridos y sea titular o apoderado.\n\n"
     
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
