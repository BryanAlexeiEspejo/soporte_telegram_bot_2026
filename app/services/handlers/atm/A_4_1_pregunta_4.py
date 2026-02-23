# app/services/handlers/atm/A_4_1_pregunta_4.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

MAX_DESC = 72
ELLIPSIS = "…"

def _short(text: str, n: int = MAX_DESC) -> str:
    text = (text or "").strip()
    return text if len(text) <= n else text[: n - 1] + ELLIPSIS

def _row(row_id: str, title: str, description: str) -> Dict:
    return {"id": row_id, "title": title, "description": _short(description)}

# ✅ Respuesta 4-1
async def manejar_A_4_1_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "*¿Qué pasa si no me acojo a la Ley?*\n"
        "R. Si dejas pasar esta oportunidad y no regularizas tu deuda hasta el 30 de abril de 2026, perderás todos los beneficios de la Ley. Esto significa que volverás a tener que pagar intereses, multas y sanciones, además de que se iniciarán los procesos de cobro.\n"
        "\n*Actualizado:*\nOctubre 15 por Yesid Flores Huayhua (ATM)\n"
        "\n*Selecciona una pregunta:*"
    )

    q16 = "¿Qué pasa si no me acojo a la Ley?"

    secciones = [
        {
            "title": "Preguntas",
            "rows": [
            _row("q-atm-4-1", "Si no me acojo", "⚠️ Consecuencias de no usar el beneficio."),
        ],
        },
        {
            "title": "Navegación",
            "rows": [
                {"id": "atm-4",    "title": "⬅️ Volver", "description": "Regresar a esta sección"},
                {"id": "atm-menu", "title": "🏛️ ATM",       "description": "Volver al menú ATM"},
                {"id": "inicio",   "title": "🏠 Inicio",    "description": "Ir al menú principal"},
            ],
        },
    ]

    payload = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text="",
        footer_text="",
        button_text="Opciones disponibles",
    )
    return [payload]
