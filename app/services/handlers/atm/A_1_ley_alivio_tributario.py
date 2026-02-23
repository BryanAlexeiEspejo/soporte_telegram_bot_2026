# app/services/handlers/atm/A_1_ley_alivio_tributario.py
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

# ✅ LISTA: 1. Sobre la Ley de Alivio Tributario (Preguntas 1–4)
async def manejar_ley_alivio_573(numero: str) -> List[Dict]:
    cuerpo = (
        "*Sobre la Ley de Alivio Tributario*\n"
        "Ley Municipal Autonómica N° 573 de Alivio Tributario.\n\n"
        "¿Qué es la Ley Municipal Autonómica N° 573 de Alivio Tributario?\n"
        "¿Quiénes pueden beneficiarse con esta Ley?\n"
        "¿Desde cuándo y hasta qué fecha está en vigencia esta Ley N° 573?\n"
        "\n*Selecciona una pregunta:*"
    )

    # Preguntas (descripciones completas)
    q1 = "¿Qué es la Ley Municipal Autonómica N° 573 de Alivio Tributario?"
    q2 = "¿Quiénes pueden beneficiarse con esta Ley?"
    q3 = "¿Desde cuándo y hasta qué fecha está en vigencia esta Ley N° 573?"
   

    secciones = [
        {
            "title": "Preguntas",
            "rows": [
                _row("q-atm-1-1", "¿Qué es la Ley 573?", "📘 Explica el alcance de la Ley de Alivio Tributario."),
                _row("q-atm-1-2", "¿Quiénes acceden?", "👥 Quién puede beneficiarse del perdonazo."),
                _row("q-atm-1-3", "Vigencia del beneficio", "⏰ Desde cuándo y hasta cuándo aplica la Ley 573."),
            ],
        },
        {
            "title": "Navegación",
            "rows": [
                {
                    "id": "atm-menu",
                    "title": "🏛️ Menú ATM",
                    "description": "Volver a Administración Tributaria Municipal – ATM",
                },
                {
                    "id": "inicio",
                    "title": "🏠 Inicio",
                    "description": "Ir al menú principal",
                },
            ],
        },
    ]

    payload = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text="",
        footer_text="",
        button_text="Ver preguntas",
    )

    await set_estado_usuario(numero, {"contexto": "atm", "estado": "atm-1"})
    return [payload]
