# app/services/handlers/atm/A_1_1_pregunta_1.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

def _row(row_id: str, title: str, desc: str) -> Dict:
    return {"id": row_id, "title": title, "description": desc}

# ✅ Respuesta 1-1
async def manejar_A_1_1_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "*¿Qué es la Ley Municipal Autonómica N° 573 de Alivio Tributario?*\n"
        "R. Es una ley aprobada por el Gobierno Autónomo Municipal de La Paz que establece un "
        "periodo voluntario de regularización y condonación tributaria. Permite a los contribuyentes "
        "ponerse al día con sus impuestos sin pagar intereses, multas ni sanciones, hasta el 30 de abril de 2026.\n"
        "\n*Actualizado:*\nOctubre 15 por Yesid Flores Huayhua (ATM)\n"
        "\n*Selecciona una pregunta:*"
    )

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
                {"id": "atm-1",    "title": "⬅️ Menú anterior", "description": "Volver a Sobre la Ley de Alivio Tributario"},
                {"id": "atm-menu", "title": "🏛️ Menú anterior", "description": "Volver a Administración Tributaria Municipal – ATM"},
                {"id": "inicio",   "title": "🏠 Inicio",         "description": "Ir al menú principal"},
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
