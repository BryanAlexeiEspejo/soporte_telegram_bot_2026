# app/services/handlers/catastro/B_2_1_info_2_B.py
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

async def manejar_info_duplicado_b(numero: str) -> List[Dict]:
    dataList: List[Dict] = []

    cuerpo = (
        "✅ *Orientación sobre los requisitos y pasos a seguir:*\n"
        "• En oficinas de la *calle Potosí y Colón*, edificio Tobia, plataforma de atención ciudadana.\n"
        "*Horario:* 8:45 hrs. a 16:15 hrs. (horario continuo).\n"
        "*Cómo llegar:* https://maps.app.goo.gl/aiTLfYVm5pUhCN5Q8\n\n"
        "✅ *Donde ingresar y recoger trámites:*\n"
        "*📍 Calle Potosí y Colón*, edificio Tobia, plataforma de atención ciudadana.\n"
        "*Horario:* 8:45 hrs. a 16:15 hrs. (horario continuo).\n"
        "*Cómo llegar:* https://maps.app.goo.gl/aiTLfYVm5pUhCN5Q8\n\n"
        "*📍 Zona Sur*, Av. Gral. José Ballivián Nº720, entre calles 13 y 14 Calacoto, Planta Baja, Edif. ATLANTA.\n"
        "*Horario:* 8:45 hrs. a 16:15 hrs. (horario continuo).\n"
        "*Cómo llegar:* https://maps.app.goo.gl/513ba6Yy9iusifVo9\n\n"
        "📄 Si cuentas con todos los documentos requeridos, solicita una ficha para *“Duplicados”* en el dispensador de fichas en esta plataforma.\n\n"
    )

    header = "¿Dónde se realiza el trámite?"
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

    await set_estado_usuario(numero, {"contexto": "catastro", "estado": "duplicado-certificado-info-b"})
    return dataList
