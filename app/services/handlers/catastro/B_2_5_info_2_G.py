# app/services/handlers/catastro/B_2_5_info_2_G.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista
from app.database.database import set_estado_usuario

MAX_DESC = 72
ELLIPSIS = "…"

def _short(text: str, n: int = MAX_DESC) -> str:
    text = (text or "").strip()
    return text if len(text) <= n else text[: n - 1] + ELLIPSIS

def _row(row_id: str, title: str, description: str) -> Dict:
    return {"id": row_id, "title": title, "description": _short(description)}

def _preguntas_section() -> Dict:
    return {
       "title": "Preguntas",
            "rows": [
                _row("dr-info-b", "¿Dónde se realiza?", "¿Dónde se realiza este trámite?"),
                _row("dr-info-c", "Definición", "¿Que es un duplicado de certificado de registro catastral?"),
                _row("dr-info-d", "Finalidad", "¿Para que sirve un certificado de registro catastral?"),
                _row("dr-info-e", "Costo", "¿Tiene un costo?"),
                _row("dr-info-f", "Resultado", "¿Qué obtengo al hacer este trámite?"),
                _row("dr-info-g", "Quiénes pueden", "¿Quién puede realizar este trámite?"),
            ],
    }

async def manejar_info_duplicado_g(numero: str) -> List[Dict]:
    dataList: List[Dict] = []

    cuerpo = (
        "📄 *¿Quién puede realizar este trámite?*\n\n"
        "• El propietario del inmueble.\n"
        "• Un apoderado legal, presentando el poder notarial correspondiente.\n\n"
        "📌 *¿Puedo realizar el trámite en nombre de otra persona?*\n"
        "Sí, puedes realizar el trámite en nombre de otra persona, pero debes presentar un poder notarial que te autorice a realizar trámites en nombre del propietario. \n\n"
        "⚠️ *Importante:*\n"
        "• Si el propietario ha fallecido, los herederos deben primero realizar la declaratoria de herederos para poder actualizar los datos del catastro.\n"
        "• En casos de propiedad compartida (varios propietarios), cualquiera de los copropietarios puede realizar el trámite, siempre y cuando cuente con los documentos necesarios y sea titular o apoderado.\n\n"
    )

    header = ""
    footer = ""

    secciones = [
        _preguntas_section(),
        {
            "title": "Navegación",
            "rows": [
                {"id": "catastro-b", "title": "⬅️ Volver", "description": "Volver al menú anterior"},
                {"id": "inicio", "title": "🏠 Inicio", "description": "Volver al Inicio"},
            ],
        },
    ]

    payload_menu = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text=header,
        footer_text=footer,
        button_text="Opciones disponibles",
    )

    dataList.append(payload_menu)

    await set_estado_usuario(numero, {"contexto": "catastro", "estado": "duplicado-certificado-info-g"})
    return dataList
