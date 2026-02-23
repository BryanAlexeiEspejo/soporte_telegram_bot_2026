from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista
from app.database.database import set_estado_usuario

async def manejar_info_copias_legalizadas_g(numero: str) -> List[Dict]:
    dataList = []

    # ✅ Cuerpo del mensaje informativo
    cuerpo = (
        "*¿Quién puede realizar este trámite?*\n"
        "• El propietario del inmueble.\n"
        "• Un apoderado legal, presentando el poder notarial correspondiente.\n"
        "\n"
        "*Información útil*\n"
        "*¿Puedo realizar el trámite en nombre de una tercera persona?*\n"
        "Sí, puedes realizar el trámite en nombre de otra persona, pero debes presentar un poder notarial que te autorice a realizar trámites en nombre del propietario.\n\n"
        "*Importante:*\n"
        "• Si el propietario ha fallecido, los herederos deben primero realizar la declaración de herederos para poder actualizar los datos del catastro.\n"
        "• En casos de propiedad compartida (varios propietarios), cualquiera de los copropietarios puede realizar el trámite, siempre y cuando cuente con los documentos necesarios y sea titular o apoderado."
    )

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

    # ✅ Crear payload de lista
    payload_lista = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text="📘 Copias Legalizadas",
        footer_text="",
        button_text="Opciones disponibles"
    )
    dataList.append(payload_lista)

    # ✅ Guardar estado
    await set_estado_usuario(numero, {
        "contexto": "catastro",
        "estado": "copias-legalizadas-info-g"
    })

    return dataList
