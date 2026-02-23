# app/services/handlers/catastro/B_2_2_info_2_C.py
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

async def manejar_info_duplicado_c(numero: str) -> List[Dict]:
    dataList: List[Dict] = []

    cuerpo = (
        "📄 *¿Qué es un duplicado de certificado de registro catastral?*\n\n"
        "El Duplicado del Certificado de Registro Catastral es un documento técnico que avala la existencia "
        "del registro de un bien inmueble en el *Módulo Catastro* del Sistema de Información Territorial "
        "del Gobierno Autónomo Municipal de La Paz (*SIT V2*).\n\n"
        "📥 Puede ser obtenido en línea desde cualquier ordenador, en cualquier lugar.\n\n"
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

    await set_estado_usuario(numero, {"contexto": "catastro", "estado": "duplicado-certificado-info-c"})
    return dataList
