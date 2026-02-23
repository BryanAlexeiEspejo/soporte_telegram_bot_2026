# app/services/handlers/atm/A_2_2_pregunta_2.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

MAX_DESC = 72
ELLIPSIS = "…"

def _short(t: str, n: int = MAX_DESC) -> str:
    t = (t or "").strip()
    return t if len(t) <= n else t[: n - 1] + ELLIPSIS

def _row(row_id: str, title: str, desc: str) -> Dict:
    return {"id": row_id, "title": title, "description": _short(desc)}

# ✅ Respuesta 2-2
async def manejar_A_2_2_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "*¿Desde qué año hasta qué año se condonarán intereses, multas y sanciones con esta Ley?*\n"
        "• Desde la gestión 2012 hasta la 2023 para Inmuebles, Vehículos.\n"
        "• Desde la gestión 1995 hasta 2023 para Transferencias Onerosas (IMT, IMTO).\n"
        "• Desde la gestión 2016 hasta la 2023 para Patentes Municipales\n"
        "\n*Actualizado:*\nOctubre 15 por Yesid Flores Huayhua (ATM)\n"
        "\n*Selecciona una pregunta:*"
    )

    q1 = "¿Qué impuestos están incluidos en esta Ley de condonación?"
    q2 = "¿Desde qué año hasta qué año se condonarán intereses, multas y sanciones con esta Ley?"
    q3 = "¿Qué beneficios obtengo si me acojo a esta Ley?"
    q4 = "¿Qué pasa si ya pagué mi deuda antes de esta Ley?"

    secciones = [
       {
            "title": "Preguntas",
            "rows": [
                _row("q-atm-2-1", "Impuestos incluidos", "💰 Qué tributos entran en el perdonazo."),
                _row("q-atm-2-2", "Período condonado", "📅 Años que cubre la condonación y el perdón."),
                _row("q-atm-2-3", "Beneficios", "✅ Ventajas de acogerse a la Ley 573."),
                _row("q-atm-2-4", "¿Ya pagaste?", "⚖️ Qué pasa si cancelaste antes de la ley."),
            ],
        },
        {"title": "Navegación", "rows": [
            {"id": "atm-2",    "title": "⬅️ Menú anterior", "description": _short("Volver a Alcance y Beneficios del Perdonazo")},
            {"id": "atm-menu", "title": "🏛️ Menú anterior", "description": _short("Volver a Administración Tributaria Municipal – ATM")},
            {"id": "inicio",   "title": "🏠 Inicio",         "description": _short("Ir al menú principal")},
        ]},
    ]

    payload = await crear_payload_lista(
        numero=numero, cuerpo=cuerpo, opciones=secciones,
        header_text="", footer_text="", button_text="Opciones disponibles"
    )
    return [payload]
