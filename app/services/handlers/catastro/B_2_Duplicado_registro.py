# app/services/handlers/catastro/B_2_Duplicado_registro.py
from typing import List, Dict
from app.database.database import set_estado_usuario
from app.services.whatsapp_template import crear_payload_lista

MAX_DESC = 72
ELLIPSIS = "…"

def _short(text: str, n: int = MAX_DESC) -> str:
    text = (text or "").strip()
    return text if len(text) <= n else text[: n - 1] + ELLIPSIS

def _row(row_id: str, title: str, description: str) -> Dict:
    return {"id": row_id, "title": title, "description": _short(description)}

async def manejar_certificado_duplicado(numero: str) -> List[Dict]:
    dataList: List[Dict] = []

    cuerpo = (
        "*📄 Requisitos para duplicado de certificado de registro catastral, para una persona natural:*\n\n"
        "Se requiere los siguientes requisitos:\n"
        "• Cédula de identidad del/de los propietarios (original y fotocopia).\n"
        "• Código catastral y/o croquis de ubicación.\n\n"
        "En oficinas de la calle Potosí y Colón, edificio Tobía, plataforma archivo catastro.\n"
        "🗺️ *Cómo llegar:* https://maps.app.goo.gl/aiTLfYVm5pUhCN5Q8\n\n"
        "*📚 Recursos y documentación:*\n"
        "Descargar fichas catastrales A, B, C.\n"
        "Normativa y leyes municipales catastrales.\n\n"
    )

    header = ""
    footer = ""

    secciones = [
        {
            "title": "Preguntas",
            "rows": [
                _row("dr-info-b", "¿Dónde se realiza?", "¿Dónde se realiza este trámite?"),
                _row("dr-info-c", "Definición", "¿Que es un duplicado de certificado de registro catastral?"),
                _row("dr-info-d", "Finalidad", "¿Para que sirve un certificado de registro catastral?"),
                _row("dr-info-e", "Costo", "¿Tiene un costo?"),
                _row("dr-info-f", "Resultado", "¿Qué obtengo al hacer este trámite?"),
                _row("dr-info-g", "Quiénes pueden", "¿Quién puede realizar este trámite?"),
            ],
        },
        {
            "title": "Recursos adicionales",
            "rows": [
                _row("info-fichas", "📥 Fichas A, B, C", "Descargar fichas catastrales A,B,C."),
                _row("info-leyes", "📘 Normativa catastral", "Normativa y leyes municipales catastro."),
            ],
        },
         {
            "title": "Navegación",
            "rows": [
                {"id": "catastro-b", "title": "⬅️ Volver", "description": "Regresar al menú anterior"},
                {"id": "inicio", "title": "🏠 Inicio", "description": "Menú principal de AMI"},
            ],
        },
    ]

    payload_menu = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text=header,
        footer_text=footer,
        button_text="Información util",
    )

    dataList.append(payload_menu)

    await set_estado_usuario(numero, {
        "contexto": "catastro",
        "estado": "duplicado-certificado-preguntas",
    })

    return dataList
