# app/services/handlers/catastro/B_5_Emision_certificado_ley247.py
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

async def manejar_emision_certificado_ley247(numero: str) -> List[Dict]:
    dataList: List[Dict] = []

    cuerpo = (
        "📄 *Requisitos para la emisión de certificado de registro catastral a través del servicio municipal de catastro en el marco de la Ley 247:*\n\n"
        "Permite a los ciudadanos poder realizar el trámite ante las Oficinas de Derechos Reales, previo cumplimiento de los requisitos señalados por dicha instancia, "
        "para la regularización de la superficie en demasía en el marco de la ley 247.\n\n"
        "🔹 *Requisitos:*\n"
        "• Certificado de registro catastral vigente (posterior a octubre de 2012).\n"
        "• Carta de solicitud (se adjunta carta modelo).\n"
        "• El bien inmueble debe estar consolidado con muro perimetral sólido.\n"
        "• Testimonio de propiedad (fotocopia).\n"
        "• Folio real o tarjeta de Propiedad (fotocopia).\n"
        "• Cédula de identidad del o los propietarios.\n"
        "• Boleta de pago de impuestos.\n\n"
    )

    header = ""
    footer = ""

    secciones = [
        {
            "title": "Preguntas",
            "rows": [
                _row("rec-info-b", "¿Dónde se realiza?", "¿Dónde se realiza este trámite?"),
                _row("rec-info-c", "Definición", "¿Que es una emisión de certificado de registro catastral a través de servicio municipal de catastro en el marco de la Ley 247?"),
                _row("rec-info-d", "Finalidad", "¿Para que sirve un certificado de registro catastral?"),
                _row("rec-info-e", "Costo", "¿Tiene costo este trámite?"),
                _row("rec-info-f", "Resultado", "¿Qué obtengo al hacer el trámite?"),
                _row("rec-info-g", "Quiénes pueden", "¿Quién puede realizar este trámite?"),
            ],
        },
        {
            "title": "Recursos adicionales",
            "rows": [
                _row("info-fichas", "📥 Fichas A, B, C", "Descargar fichas catastrales A,B,C."),
                _row("info-leyes", "📘 Normativas legales", "Normativa y leyes municipales catastro."),
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
        "estado": "emision-certificado-ley247-preguntas",
    })

    return dataList
