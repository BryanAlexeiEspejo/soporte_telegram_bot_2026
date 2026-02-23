# app/services/handlers/atm/A_2_4_pregunta_2.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

MAX_DESC = 72
ELLIPSIS = "…"

def _short(t: str, n: int = MAX_DESC) -> str:
    t = (t or "").strip()
    return t if len(t) <= n else t[: n - 1] + ELLIPSIS

def _row(row_id: str, title: str, desc: str) -> Dict:
    return {"id": row_id, "title": title, "description": _short(desc)}

# ✅ Respuesta 2-4
async def manejar_A_2_4_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "*¿Qué pasa si ya pagué mi deuda antes de esta Ley?*\n"
        "R. Si ya realizaste el pago total de tus tributos antes de la vigencia de la Ley N° 573, "
        "no necesitas acogerte al beneficio, ya que tu deuda se encuentra regularizada y no tienes "
        "obligaciones pendientes con el Gobierno Autónomo Municipal de La Paz. La Ley de Alivio "
        "Tributario está dirigida únicamente a quienes aún tienen deudas por pagar.\n"
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
